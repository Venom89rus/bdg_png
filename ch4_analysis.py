import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd  # Обязательно подключаем pandas

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

    # График: распределение содержания метана по диапазонам
    st.markdown("### 📊 Распределение содержания CH₄ по диапазонам (%)")

    # Определяем диапазоны
    bins = [0, 20, 40, 60, 70, 80, 90, 100]
    labels = [f"{bins[i]}–{bins[i+1]}" for i in range(len(bins) - 1)]
    df['CH4_range'] = pd.cut(df["Метан"], bins=bins, labels=labels, include_lowest=True)

    # Группировка и фильтрация
    ch4_counts = df['CH4_range'].value_counts().sort_index()
    ch4_counts = ch4_counts[ch4_counts > 0]  # убираем диапазоны без данных

    # Построение графика
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(ch4_counts.index.astype(str), ch4_counts.values, color='blue')
    ax.set_xlabel("Количество отборов")
    ax.set_ylabel("Диапазон содержания CH₄, %")
    ax.set_title("Распределение содержания метана по диапазонам")
    for i, v in enumerate(ch4_counts.values):
        ax.text(v + 0.5, i, str(v), va='center', fontsize=9)
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
