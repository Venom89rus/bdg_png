import streamlit as st
import matplotlib.pyplot as plt

def run():
    df = st.session_state.get("filtered_df", None)
    if df is None or df.empty:
        st.warning("Нет данных для анализа.")
        return

    st.subheader("Анализ С₅+в.")
    st.info(f"🔢 Количество записей для анализа: {len(df)}")

    components = ["и-Пентан", "н-Пентан", "Гексаны", "Гептаны", "Октаны"]
    for comp in components:
        if comp not in df.columns:
            st.warning(f"Компонент {comp} не найден в данных.")
            return

    # Молярные массы (г/моль)
    molar_masses = {
        "и-Пентан": 72.15,
        "н-Пентан": 72.15,
        "Гексаны": 86.18,
        "Гептаны": 100.2,
        "Октаны": 114.23
    }

    Vm = 0.022414  # м³/моль — молярный объем при н.у.

    # Корректный расчет массовой концентрации (г/м³)
    for comp in components:
        df[comp + "_g_m3"] = df[comp] / 100 * molar_masses[comp] / Vm

    df["С5+в."] = df[[f"{c}_g_m3" for c in components]].sum(axis=1)

    # 📊 Статистика
    st.markdown("### 📈 Статистика по С₅+в.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Среднее", f"{df['С5+в.'].mean():.2f} г/м³")
    col2.metric("Максимум", f"{df['С5+в.'].max():.2f} г/м³")
    col3.metric("Минимум", f"{df['С5+в.'].min():.2f} г/м³")

    # 📊 График
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df.index.astype(str), df["С5+в."], color='blue')
    ax.set_title("Содержание С₅+в. (г/м³)")
    ax.set_xlabel("Номер отбора")
    ax.set_ylabel("С₅+в., г/м³")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # 🧾 Таблица
    display_cols = [col for col in ["Месторождение", "ДНС", "Ступень отбора", "Дата протокола"] if col in df.columns]
    df_display = df[display_cols + components + ["С5+в."]].copy()
    df_display["С5+в."] = df_display["С5+в."].round(2)

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

    st.markdown(f'<div class="scroll-free-table">{df_display.to_html(index=False)}</div>', unsafe_allow_html=True)
