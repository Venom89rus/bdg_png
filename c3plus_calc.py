import streamlit as st
import matplotlib.pyplot as plt

def run():
    df = st.session_state.get("filtered_df", None)
    if df is None or df.empty:
        st.warning("Нет данных для анализа.")
        return

    st.subheader("Анализ С₃+в.")
    st.info(f"🔢 Количество записей для анализа: {len(df)}")

    components = ["Пропан", "и-Бутан", "н-Бутан", "и-Пентан", "н-Пентан", "Гексаны", "Гептаны", "Октаны"]
    for comp in components:
        if comp not in df.columns:
            st.warning(f"Компонент {comp} не найден в данных.")
            return

    # Молярные массы (г/моль)
    molar_masses = {
        "Пропан": 44.1,
        "и-Бутан": 58.12,
        "н-Бутан": 58.12,
        "и-Пентан": 72.15,
        "н-Пентан": 72.15,
        "Гексаны": 86.18,
        "Гептаны": 100.2,
        "Октаны": 114.23
    }

    Vm = 0.022414  # м³/моль — молярный объем при н.у.

    # Корректный расчет: переводим мольные % в доли, затем пересчет в г/м³
    for comp in components:
        df[comp + "_g_m3"] = df[comp] / 100 * molar_masses[comp] / Vm

    df["С3+в."] = df[[f"{c}_g_m3" for c in components]].sum(axis=1)

    # Статистика
    st.markdown("### 📈 Статистика по С₃+в.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Среднее", f"{df['С3+в.'].mean():.2f} г/м³")
    col2.metric("Максимум", f"{df['С3+в.'].max():.2f} г/м³")
    col3.metric("Минимум", f"{df['С3+в.'].min():.2f} г/м³")

    # График
    df = df.reset_index(drop=True)
    df["Отбор"] = df.index + 1

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df["Отбор"], df["С3+в."], color='orange')
    ax.set_title("Содержание С₃+в. (г/м³) по отборам")
    ax.set_xlabel("№ отбора")
    ax.set_ylabel("С₃+в., г/м³")
    st.pyplot(fig)

    # Таблица
    display_cols = [col for col in ["Месторождение", "ДНС", "Ступень отбора", "Дата протокола"] if col in df.columns]
    df_display = df[display_cols + components + ["С3+в."]].copy()
    df_display["С3+в."] = df_display["С3+в."].round(2)

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
