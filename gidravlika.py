import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

@st.cache_data
def load_data():
    return pd.read_excel("Pipe_size.xlsx", sheet_name="Лист1")

def run_hydraulic_calc():
    st.title("🔧 Гидравлический расчет трубопровода")

    df = load_data()

    # Очистка данных и исправление названий столбцов
    df = df.dropna(subset=["Регион", "Месторождение ", "Объект подготовки", "Начало "])

    # Фильтры по данным
    region = st.selectbox("Выберите регион:", df["Регион"].unique())
    df_region = df[df["Регион"] == region]

    field = st.selectbox("Выберите месторождение:", df_region["Месторождение "].unique())
    df_field = df_region[df_region["Месторождение "] == field]

    plant = st.selectbox("Выберите объект подготовки:", df_field["Объект подготовки"].unique())
    df_plant = df_field[df_field["Объект подготовки"] == plant]

    start_point = st.selectbox("Выберите начало участка:", df_plant["Начало "].unique())
    pipe_row = df_plant[df_plant["Начало "] == start_point]

    # Отображение характеристик трубы
    st.subheader("📌 Характеристики трубы:")
    length = pipe_row["Протяженность"].values[0]
    diameter = pipe_row["Диаметр коллектора"].values[0]
    thickness = pipe_row["Толщина стенки"].values[0]
    st.markdown(f"- Протяженность: **{length} м**")
    st.markdown(f"- Диаметр: **{diameter} мм**")
    st.markdown(f"- Толщина стенки: **{thickness} мм**")

    # Ввод параметров газа
    st.subheader("🛠️ Параметры газа:")
    pressure = st.number_input("Давление газа (МПа)", min_value=0.7)
    flow = st.number_input("Расход газа (тыс. м³/сут)", min_value=100)
    t_gas = st.number_input("Температура газа (°C)", min_value=30.0)
    t_soil = st.number_input("Температура грунта (°C)", min_value=-5.0)
    humidity = st.number_input("Содержание влаги (%)", min_value=0.02)
    density = st.number_input("Плотность газа (кг/м³)", min_value=0.9)

    st.divider()

    if st.button("🚀 Посчитать гидравлику"):
        if all([pressure, flow, t_gas, t_soil, humidity, density]):
            # Перевод единиц и расчёты
            diameter_m = diameter / 1000  # мм → м
            velocity = flow * 1000 / (86400 * 3.14 * (diameter_m / 2) ** 2)
            friction_loss = 0.02 * (length / diameter_m) * (density * velocity ** 2) / 2 / 1e5 / 10  # Примерная формула

            # Вывод метрик
            st.success("✅ Расчет выполнен успешно!")
            st.metric("Потери давления", f"{friction_loss:.2f} МПа")
            st.metric("Скорость газа", f"{velocity:.2f} м/с")

            # Визуализация падения давления и скорости
            step = 10  # шаг по длине, м
            x_vals = list(range(0, int(length) + step, step))
            pressure_vals = []
            velocity_vals = []

            for x in x_vals:
                local_loss = friction_loss * (x / length)
                local_pressure = pressure - local_loss
                pressure_vals.append(local_pressure)
                velocity_vals.append(velocity)  # скорость неизменна при постоянном расходе

            # График
            fig, ax1 = plt.subplots(figsize=(8, 5))
            ax1.plot(x_vals, pressure_vals, label="Давление (МПа)", color="blue")
            ax1.set_xlabel("Длина трубы (м)")
            ax1.set_ylabel("Давление (МПа)", color="blue")
            ax1.tick_params(axis="y", labelcolor="blue")
            ax1.set_title("📉 Падение давления и скорость газа по длине трубы")

            ax2 = ax1.twinx()
            ax2.plot(x_vals, velocity_vals, label="Скорость (м/с)", color="green", linestyle="--")
            ax2.set_ylabel("Скорость (м/с)", color="green")
            ax2.tick_params(axis="y", labelcolor="green")

            fig.tight_layout()
            st.pyplot(fig)

        else:
            st.error("❌ Не вся информация указана для расчета гидравлики")

if __name__ == "__main__":
    run_hydraulic_calc()
