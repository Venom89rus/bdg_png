import streamlit as st
import numpy as np                          # для массивов и графиков
import pandas as pd                         # для таблиц и экспорта
import matplotlib.pyplot as plt             # построение графиков
from CoolProp.CoolProp import HAPropsSI     # расчет точки росы и влажности
import math
from io import BytesIO                      # для хранения файла в памяти
import xlsxwriter                           # экспорт Excel

def run_methanol_calc():

    st.set_page_config(page_title="Расчет метанола и точки росы", layout="wide")
    st.title("💧 Расчет подачи метанола и точки росы воды (с использованием CoolProp)")

    # --- Ввод данных ---
    st.sidebar.header("Входные данные")
    pressure = st.sidebar.slider("Давление (МПа)", 1.0, 20.0, 5.0)
    temperature = st.sidebar.slider("Температура газа (°C)", -20.0, 40.0, 5.0)
    gas_flow = st.sidebar.number_input("Расход газа (м³/сут)", min_value=1.0, value=100000.0)

    dew_mode = st.sidebar.radio("Учет воды", ["Измеренное содержание (г/м³)", "По точке росы"])
    if dew_mode == "Измеренное содержание (г/м³)":
        water_content = st.sidebar.number_input("Содержание воды (г/м³)", min_value=0.0, value=20.0)
    else:
        dew_point = st.sidebar.number_input("Точка росы воды (°C)", value=0.0)
        RH = 1.0  # насыщение
        try:
            water_content = HAPropsSI("W", "T", dew_point + 273.15, "P", pressure * 1e6, "R", RH) * 1000 * 18.015
        except:
            water_content = 0

    # --- Состав газа (мольные доли) ---
    st.sidebar.markdown("### Состав газа (моль)")
    composition = {
        "CH4": st.sidebar.slider("CH₄", 0.0, 1.0, 0.9),
        "C2H6": st.sidebar.slider("C₂H₆", 0.0, 1.0, 0.05),
        "C3H8": st.sidebar.slider("C₃H₈", 0.0, 1.0, 0.03),
        "C4H10": st.sidebar.slider("C₄H₁₀", 0.0, 1.0, 0.01),
        "C5H12": st.sidebar.slider("C₅H₁₂", 0.0, 1.0, 0.005),
        "C6+": st.sidebar.slider("C₆⁺", 0.0, 1.0, 0.005)
    }
    # После ввода состава газа выполняем нормализацию, т.е. приводим состав к сумме 1 (если введено с ошибкой)
    total = sum(composition.values())
    composition = {k: v / total for k, v in composition.items()}

    # --- Температура гидратов ---
    A = -13.7 # А и В эмпирические коэффициенты, зависящие от состава газа.
    B = 30.5
    t_hydrate = A * math.log(pressure) + B

    # --- Расчет подачи метанола ---
    result = {}
    if temperature < t_hydrate:
        delta_T = t_hydrate - temperature
        K = 0.86                                                # коэф. Хаммершмидта, отражает эффективность ингибирования метанолом.
        w_meoh = delta_T / K                                    # массовая доля метанола, необходимая для предотвращения гидратообразования, в процентах от массы воды в газе.
        water_mass_kg = (water_content / 1000) * gas_flow       # масса воды кг/сут
        methanol_mass_kg = water_mass_kg * (w_meoh / 100)       # масса метанола в сутки кг.
        methanol_density = 792.0                                # Плотнось метанола кг/м3
        methanol_vol_liters = methanol_mass_kg / (methanol_density / 1000) # объём метанола л/сут.
        result.update({
            "Темп. гидратов (°C)": t_hydrate,
            "ΔT (°C)": delta_T,
            "Содержание воды (г/м³)": water_content,
            "Метанол, кг/сут": methanol_mass_kg,
            "Метанол, л/сут": methanol_vol_liters
        })
    else:
        result.update({
            "Темп. гидратов (°C)": t_hydrate,
            "Сообщение": "Гидраты не образуются — подача метанола не требуется."
        })

    st.subheader("📋 Результаты расчета")
    st.write(pd.DataFrame([result]))

    # --- График ---
    pressures = np.linspace(1, 20, 100)
    hydrate_temps = A * np.log(pressures) + B
    fig, ax = plt.subplots()
    ax.plot(pressures, hydrate_temps, label="Темп. образования гидратов")
    ax.axhline(temperature, color='r', linestyle='--', label="T газа")
    ax.set_xlabel("Давление (МПа)")
    ax.set_ylabel("Температура (°C)")
    ax.grid(True)
    ax.legend()
    st.pyplot(fig)

    # --- Экспорт в Excel ---
    def to_excel(data):
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        pd.DataFrame([data]).to_excel(writer, index=False, sheet_name='Расчет')
        writer.close()
        return output.getvalue()

    excel_data = to_excel(result)
    st.download_button("📥 Скачать Excel", data=excel_data, file_name="hydrate_calc.xlsx", mime="application/vnd.ms-excel")

if __name__ == "__main__":
    run_methanol_calc()