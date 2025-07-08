import streamlit as st  # Импортируем библиотеку Streamlit для создания веб-приложения
import matplotlib.pyplot as plt  # Импортируем библиотеку matplotlib для построения графиков
import numpy as np  # Импортируем библиотеку NumPy для численных вычислений (не используется в коде)
import pandas as pd  # Импортируем pandas для работы с таблицами

def run():
    # Получаем отфильтрованные данные из session_state
    df = st.session_state.get("filtered_df", None)
    if df is None or df.empty:
        st.warning("Нет данных для анализа.")  # Предупреждение, если данных нет
        return

    st.subheader("Анализ С₅+в.")  # Заголовок раздела анализа
    st.info(f"🔢 Количество записей для анализа: {len(df)}")  # Вывод количества записей

    # Список компонентов, входящих в С₅+в.
    components = ["и-Пентан", "н-Пентан", "Гексаны", "Гептаны", "Октаны"]

    # Проверяем наличие всех компонентов в DataFrame
    for comp in components:
        if comp not in df.columns:
            st.warning(f"Компонент {comp} не найден в данных.")  # Предупреждение, если компонент отсутствует
            return

    # Молярные массы (г/моль) для расчета массовой концентрации
    molar_masses = {
        "и-Пентан": 72.15,
        "н-Пентан": 72.15,
        "Гексаны": 86.18,
        "Гептаны": 100.2,
        "Октаны": 114.23
    }

    Vm = 0.022414  # м³/моль — молярный объём газа при нормальных условиях

    # Расчет массовой концентрации каждого компонента (в г/м³)
    for comp in components:
        df[comp + "_g_m3"] = df[comp] / 100 * molar_masses[comp] / Vm  # Преобразуем объёмную долю в массовую концентрацию

    # Суммируем массовые концентрации по всем компонентам → получаем С₅+в.
    df["С5+в."] = df[[f"{c}_g_m3" for c in components]].sum(axis=1)  # Итоговое значение С₅+в.

    # 📈 Выводим базовую статистику по С₅+в.
    st.markdown("### 📈 Статистика по С₅+в.")
    col1, col2, col3 = st.columns(3)  # Создаем три колонки для вывода статистики
    col1.metric("Среднее", f"{df['С5+в.'].mean():.2f} г/м³")  # Среднее значение
    col2.metric("Максимум", f"{df['С5+в.'].max():.2f} г/м³")  # Максимальное значение
    col3.metric("Минимум", f"{df['С5+в.'].min():.2f} г/м³")  # Минимальное значение

    # 📊 Горизонтальная гистограмма по интервалам (50, 100, 150 …)
    st.markdown("### 📊 Распределение концентрации С₅+в.")

    step = 50  # Шаг интервалов в г/м³
    max_value = df["С5+в."].max()  # Находим максимальное значение
    bins = list(range(0, int(max_value) + step, step))  # Формируем интервалы

    # Группируем данные по интервалам (категоризируем значения)
    df["interval"] = pd.cut(df["С5+в."], bins=bins)  # Разбиваем данные на интервалы

    # Считаем количество записей в каждом интервале
    counts = df["interval"].value_counts().sort_index()  # Считаем частоты интервалов

    # Отфильтровываем пустые интервалы (где count == 0)
    counts = counts[counts > 0]  # Убираем нулевые интервалы

    # Строим горизонтальную гистограмму
    fig, ax = plt.subplots(figsize=(10, 6))  # Создаем фигуру и ось для графика

    for i, (interval, count) in enumerate(counts.items()):  # Для каждого интервала
        label = f"{int(interval.left)}–{int(interval.right)}"  # Формируем подпись интервала
        ax.barh(y=label, width=count, height=0.8, color='blue', edgecolor='black')  # Рисуем горизонтальный столбик
        ax.text(count + 0.5, i, str(count), va='center', fontsize=10)  # Подписываем количество отборов

    ax.set_title("Распределение содержания С₅+в. (г/м³)")  # Заголовок графика
    ax.set_xlabel("Количество отборов")  # Подпись оси X
    ax.set_ylabel("Интервалы С₅+в., г/м³")  # Подпись оси Y

    st.pyplot(fig)  # Отображаем график в Streamlit

    # 🧾 Таблица с результатами
    display_cols = [col for col in ["Месторождение", "ДНС", "Ступень отбора", "Дата протокола"] if col in df.columns]  # Определяем доступные колонки для отображения
    df_display = df[display_cols + components + ["С5+в."]].copy()  # Формируем таблицу для отображения
    df_display["С5+в."] = df_display["С5+в."].round(2)  # Округляем значения С₅+в.

    # Добавляем CSS для красивой таблицы
    st.markdown("""
        <style>
            .scroll-free-table table {
                width: 100% !important;
                table-layout: auto !important;
                border-collapse: collapse;
            }
            .scroll-free-table th, .scroll-free-table td {
                text-align: left;
                padding: 6px 10px;
                font-size: 14px;
                border: 1px solid #ddd;
            }
        </style>
    """, unsafe_allow_html=True)

    # Отображаем HTML-таблицу с данными
    st.markdown(f'<div class="scroll-free-table">{df_display.to_html(index=False)}</div>', unsafe_allow_html=True)