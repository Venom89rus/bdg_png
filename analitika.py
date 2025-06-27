import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from ch4_analysis import run as run_ch4
from c3plus_calc import run as run_c3
from c5plus_calc import run as run_c5

def run_analytics():
    st.title("📊 Анализ компонентного состава")

    st.markdown("### 🔍 Выберите источник данных:")
    mode = st.radio("Режим анализа:", ["База данных", "Ручной ввод"])

    if mode == "База данных":
        df = pd.read_excel("grid.xlsx")

        fields = {}
        if "Месторождение" in df.columns:
            fields['Месторождение'] = st.multiselect("Выберите месторождение:", df['Месторождение'].unique())
        if "ДНС" in df.columns:
            fields['ДНС'] = st.multiselect("Выберите ДНС:", df['ДНС'].unique())
        if "Ступень отбора" in df.columns:
            fields['Ступень отбора'] = st.multiselect("Выберите ступень отбора:", df['Ступень отбора'].unique())

        filtered_df = df.copy()
        for key, values in fields.items():
            if values:
                filtered_df = filtered_df[filtered_df[key].isin(values)]

        st.session_state["filtered_df"] = filtered_df

        st.write("## Выберите тип анализа:")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Анализ СН₄"):
                run_ch4()
        with col2:
            if st.button("Анализ С₃+в"):
                run_c3()
        with col3:
            if st.button("Анализ С₅+в"):
                run_c5()

    elif mode == "Ручной ввод":
        st.info("📝 Режим ручного ввода пока находится в разработке.")
