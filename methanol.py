import streamlit as st
import numpy as np                          # для массивов и графиков
import pandas as pd                         # для таблиц и экспорта
import matplotlib.pyplot as plt             # построение графиков
from CoolProp.CoolProp import HAPropsSI     # расчет точки росы и влажности
import math
from io import BytesIO                      # для хранения файла в памяти
import xlsxwriter                           # экспорт Excel

def run_methanol_calc():
    # Установка ширины страницы на всю ширину экрана
    st.set_page_config(layout="wide")

    # --- Ввод ключа OpenWeatherMap ---
    st.sidebar.subheader("Погода")
    weather_api_key = st.sidebar.text_input("Введите API ключ OpenWeatherMap",
                                            type="password")  # type="password" означает, что текст будет скрыт (как пароль).
    location = st.sidebar.text_input("Введите название населённого пункта",
                                     value="Муравленко")  # Ввод города или необходимых координат, поумолчанию Муравленко

    ground_temp = None
    if weather_api_key and location:  # Проверка: если пользователь ввёл и API-ключ, и название города, тогда продолжаем выполнение.
        try:
            weather_url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}&units=metric"  # Формируется URL для запроса к OpenWeatherMap API
            response = requests.get(weather_url)  # Отправляется HTTP GET-запрос по сформированному адресу
            weather_data = response.json()  # Ответ сервера (в формате JSON) преобразуется в словарь Python
            if "main" in weather_data:  # Проверка, есть ли в ответе секция "main" (где хранятся температурные данные)
                ground_temp = weather_data["main"][
                                  "temp"] - 3  # Берётся температура воздуха (weather_data["main"]["temp"]) и от неё вычитается 3°C, чтобы приблизительно оценить температуру грунта (так как она обычно немного ниже температуры воздуха).
                st.sidebar.success(
                    f"Температура грунта: {ground_temp:.1f} °C")  # Если всё прошло успешно, отображается результат в сайдбаре — температура грунта, округлённая до одного знака после запятой.
        except Exception as e:
            st.sidebar.error("Ошибка при получении данных о погоде")

            # --- Загрузка данных Excel ---
    uploaded_file = st.sidebar.file_uploader("Загрузите Excel файл с данными",
                                             type="xlsx")  # Размещаем в боковой панели slidebar
    if uploaded_file:  # Проверяем загружен ли файл. Если файл действительно загружен (то есть uploaded_file не None), тогда выполняется следующий блок кода.
        excel_data = pd.ExcelFile(
            uploaded_file)  # Загружает Excel-файл в оперативную память и позволяет работать с ним без немедленного считывания всех листов.

        df = excel_data.parse(
            'dhtmlxGrid')  # Загружает в память конкретный лист Excel-файла с названием dhtmlxGrid, результат сохраняется в переменной df, которая становится таблицей данных

        if 'Дата протокола' in df.columns:  # Проверяет, есть ли в таблице столбец с названием Дата протокола
            df['Дата протокола'] = pd.to_datetime(df['Дата протокола'],
                                                  errors='coerce')  # Приводит значения этого столбца к формату даты и времени, т.е. преобразует строки или числа в даты

        # --- Выбор Месторождения, ДНС и ступени ---
        st.sidebar.subheader("Выбор параметров")
        field = st.sidebar.selectbox("Выберите месторождение", df[
            'Месторождение'].unique())  # Создаёт выпадающий список в сайдбаре с надписью: "Выберите месторождение". df['Месторождение'].unique() — извлекает список уникальных месторождений из исходного DataFrame df
        df_field = df[df[
                          'Месторождение'] == field]  # Отфильтровывает DataFrame, оставляя только строки, соответствующие выбранному месторождению

        dns = st.sidebar.selectbox("Выберите объект подготовки (ДНС)", df_field[
            'ДНС'].unique())  # Создаёт второй выпадающий список. Извлекает уникальные значения ДНС, только среди строк выбранного месторождения (df_field)
        df_dns = df_field[df_field[
                              'ДНС'] == dns]  # Ещё одно фильтрование: оставляет только те строки, где объект подготовки соответствует выбранному (dns)

        stage = st.sidebar.selectbox("Укажите ступень отбора",
                                     df_dns['Ступень отбора'].unique())  # Аналогично выбору объекта подготовки
        selected_df = df_dns[df_dns['Ступень отбора'] == stage]

        selected_row = selected_df.iloc[
            -1]  # Берётся последняя строка из selected_df — предположительно, самая последняя (актуальная) запись. Потому что, как правило, данные хранятся в хронологическом порядке.

        st.markdown(f"""                       
        ### Месторождение: {field}                
        ### Объект подготовки: {dns}
        ### Ступень отбора: {stage}
        """)  # Текстовый вывод параметров, выбранных пользователем.

        # --- Параметры газа ---
        gas_density = selected_row['Плотность реального газа']  # Берется значение с таблицы
        gas_flow = st.sidebar.number_input("Расход газа (м³/сут)", min_value=1.0,
                                           value=100000.0)  # Расход задается в ручную

        composition = {k: selected_row[k] if k in selected_row else 0.0 for k in [
            "Метан", "Этан", "Пропан", "и-Бутан", "н-Бутан", "и-Пентан", "н-Пентан",
            "Гексаны", "Гептаны", "Октаны", "Кислород", "Водород", "Гелий", "Азот"
        ]}  # Создаётся словарь composition, где:Ключ (k) — это имя компонента газа, Значение (v) — это содержание соответствующего компонента в данных (selected_row[k]). Если компонента нет в строке то присваивается значение 0,0

        total_mol = sum(composition.values())
        if total_mol == 0:
            st.error("Сумма компонент газа равна нулю. Проверьте данные!")
            st.stop()  # Если выходит ошибка, то выполнение программы останавливается
        composition = {k: v / total_mol for k, v in
                       composition.items()}  # Все значения из словаря composition делятся на total_mol, чтобы привести их к долям от 1.0

        # Давление и температура газа
        pressure = st.sidebar.slider("Давление (МПа)", 1.0, 10.0, 6.0)  # Создаем ползунок для выбора давления
        gas_temp = st.sidebar.slider("Температура газа (°C)", 0.0, 60.0, 5.0)  # Создаем ползунок для выбора температуры
        effective_temp = min(gas_temp,
                             ground_temp if ground_temp is not None else gas_temp)  # Выбирается наименьшее значение между температурой газа и температурой грунта, используем минимальную температуру, поскольку именно при ней возможна конденсация воды
        T_K = effective_temp + 273.15  # Переводит температуру из градусов Цельсия в Кельвины
        P_Pa = pressure * 1e6  # Переводит давление из мегапаскалей (МПа) в паскали (Па), потому что в инженерных библиотеках (как CoolProp) давление часто указывается в паскалях

        # Влажность
        st.sidebar.subheader("Влажность газа")
        dew_mode = st.sidebar.radio("Источник данных о воде", ["Измеренное содержание (г/м³)",
                                                               "По точке росы (°C)"])  # Пользователю предлагается выбрать, откуда будет вводиться информация о влажности
        if dew_mode == "Измеренное содержание (г/м³)":
            measured_water_content = st.sidebar.number_input("Содержание воды (г/м³)", min_value=0.0, value=20.0)
        else:
            dew_point = st.sidebar.number_input("Точка росы (°C)",
                                                value=0.0)  # Расчет по точке росы, то пользователь вводит её значение (например, 0 °C)
            try:
                RH = 1.0  # Выполняется расчет концентрации воды с помощью библиотеки CoolProp,
                w_kg_kgdryair = HAPropsSI("W", "T", dew_point + 273.15, "P", P_Pa, "R",
                                          RH)  # HAPropsSI(...) — функция расчета влажности воздуха по параметрам
                measured_water_content = w_kg_kgdryair * 1000 * 18.015
            except:
                measured_water_content = 0.0
                st.warning("Ошибка расчета по точке росы")

        try:
            max_w_kg_kgdryair = HAPropsSI("W", "T", T_K, "P", P_Pa, "R",
                                          1.0)  # Вычисляется максимальное влагосодержание при текущей температуре и давлении (100% влажность), предельно допустимая концентрация водяного пара в газе, выше которой начинается конденсация (конденсат в трубопроводе).
            max_water_g_m3 = max_w_kg_kgdryair * 1000 * 18.015
        except:
            max_water_g_m3 = None

        result = {
            "Давление (МПа)": pressure,
            "Температура (°C)": effective_temp,
            "Содержание воды (г/м³)": measured_water_content,
            "Макс. допустимое содержание воды (г/м³)": max_water_g_m3
        }  # Сохраняем базовые данные в словарь result, который потом отобразим в таблице

        if max_water_g_m3 is not None:  # Если расчет допустимой влаги выполнен (max_water_g_m3 не None) и фактическое содержание воды превышает допустимое, начинаем расчет
            if measured_water_content > max_water_g_m3:
                excess_water = measured_water_content - max_water_g_m3  # Разница между фактическим и допустимым уровнем
                excess_water_kg = (
                                              excess_water / 1000) * gas_flow * gas_density  # Перевод избытка влаги в массу в килограммах: excess_water / 1000 — в кг/м³, gas_flow — объем газа в м³/сут, gas_density — масса 1 м³ газа
                methanol_mass_kg = excess_water_kg * 1.1  # На подачу метанола берется 110% от массы воды — технологический запас 10%
                methanol_density = 792.0  # Плотность метанола кг/м3
                methanol_vol_liters = methanol_mass_kg / (methanol_density / 1000)  # Перевод массы метанола в литры.
                optimal_methanol = methanol_vol_liters * 0.85  # Оптимизация расхода метанола. Можно уменьшить подачу на 15%, чтобы избежать перерасхода.
                economy = methanol_vol_liters - optimal_methanol  # Сколько литров можно сэкономить.

                result[
                    "Избыток влаги (г/м³)"] = excess_water  # Все расчеты добавляются в словарь result, затем он выводится в таблицу
                result["Метанол, кг/сут"] = methanol_mass_kg
                result["Метанол, л/сут"] = methanol_vol_liters
                result["Оптимальный расход метанола (л/сут)"] = optimal_methanol
                result["Потенциальная экономия (л/сут)"] = economy

                st.success(
                    "💧 Требуется подача метанола")  # Преобразуем словарь result в таблицу и выводим в интерфейсе.
            else:
                st.success("Влага в норме — подача метанола не требуется")
        else:
            st.warning("Не удалось рассчитать максимально допустимое содержание влаги.")

        st.subheader("📋 Результаты расчета")  # Преобразуем словарь result в таблицу и выводим в интерфейсе.
        result_df = pd.DataFrame([result])
        st.dataframe(result_df, use_container_width=True)

        st.subheader(
            "📊 График расхода метанола")  # Если метанол рассчитан: Строится столбчатая диаграмма. Сравниваются: фактический расчёт и оптимальный (экономичный) расход.
        if "Метанол, л/сут" in result:
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.bar(["Фактический"], [result["Метанол, л/сут"]], color='blue', label='Фактический')
            ax.bar(["Оптимальный"], [result["Оптимальный расход метанола (л/сут)"]], color='green', label='Оптимальный')
            ax.set_ylabel("Метанол, л/сут")
            ax.set_title("Сравнение расхода метанола")
            ax.legend()
            st.pyplot(fig, use_container_width=True)

        # --- Экспорт в Excel ---
        display_columns = [
            "Дата протокола", "Номер протокола", "Метан", "Этан", "Пропан", "и-Бутан", "н-Бутан",
            "и-Пентан", "н-Пентан", "Гексаны", "Гептаны", "Октаны", "Кислород", "Водород", "Гелий", "Азот"
        ]
        output = BytesIO()  # BytesIO() создаёт буфер в оперативной памяти — по сути, "виртуальный файл", который не записывается на диск. Он нужен для временного хранения Excel-файла перед тем, как передать его пользователю через кнопку скачивания.
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:  # Создание Excel-файла с двумя листами
            result_df.to_excel(writer, index=False, sheet_name='Расчет')
            selected_df[display_columns].to_excel(writer, index=False, sheet_name='Компоненты')
        st.download_button(
            label="Скачать отчет в Excel",
            data=output.getvalue(),
            file_name=f"отчет_метанол_{field}_{dns}_{stage}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )  # Кнопка скачивания Excel-файла. mime=... — MIME-тип для Excel-файлов (нужно, чтобы браузер понял тип содержимого).

        # --- Отображение таблицы компонентов ---
        st.subheader("📑 Исходные данные")
        st.dataframe(selected_df[display_columns], use_container_width=True)  # Отображения таблицы в веб-интерфейсе.

if __name__ == "__main__":
    run_methanol_calc()