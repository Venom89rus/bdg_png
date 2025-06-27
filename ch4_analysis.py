import streamlit as st
import matplotlib.pyplot as plt

def run():
    df = st.session_state.get("filtered_df", None)
    if df is None or df.empty:
        st.warning("Нет данных для анализа.")
        return

    st.subheader("Анализ СН₄")
    st.info(f"🔢 Количество записей для анализа: {len(df)}")

    if "Метан" not in df.columns:
        st.warning("Компонент CH₄ не найден в данных.")
        return

    # График
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df.index, df["Метан"], marker='o', linestyle='-', color='green')
    ax.set_title("Содержание СН₄")
    ax.set_xlabel("Индекс")
    ax.set_ylabel("CH₄, %")
    st.pyplot(fig)

    # Статистика
    st.markdown("### 📈 Статистика по CH₄")
    col1, col2, col3 = st.columns(3)
    col1.metric("Среднее", f"{df['Метан'].mean():.2f} %")
    col2.metric("Максимум", f"{df['Метан'].max():.2f} %")
    col3.metric("Минимум", f"{df['Метан'].min():.2f} %")

    # Таблица
    display_cols = [col for col in ["Месторождение", "ДНС", "Ступень отбора", "Дата протокола"] if col in df.columns]
    df_display = df[display_cols + ["Метан"]].copy()
    df_display["Метан"] = df_display["Метан"].round(2)

    # CSS для таблицы без скролла
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
