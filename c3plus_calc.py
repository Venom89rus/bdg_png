# Импортируем необходимые библиотеки
import streamlit as st  # Интерфейс Streamlit
import matplotlib.pyplot as plt  # Построение графиков
import pandas as pd  # Работа с табличными данными

# Основная функция анализа С₃+в
def run():
    # Получаем отфильтрованный датафрейм из сессионного состояния (загруженный в основном файле)
    df = st.session_state.get("filtered_df", None)

    # Если данных нет или датафрейм пустой, показываем предупреждение и прекращаем выполнение
    if df is None or df.empty:
        st.warning("Нет данных для анализа.")
        return

    # Заголовок раздела
    st.subheader("Анализ С₃+в.")
    # Информация о количестве записей, доступных для анализа
    st.info(f"🔢 Количество записей для анализа: {len(df)}")

    # Задаем список углеводородных компонентов, входящих в С₃+в.
    components = ["Пропан", "и-Бутан", "н-Бутан", "и-Пентан", "н-Пентан", "Гексаны", "Гептаны", "Октаны"]

    # Проверка наличия всех нужных компонентов в таблице
    for comp in components:
        if comp not in df.columns:
            st.warning(f"Компонент {comp} не найден в данных.")
            return  # если хотя бы одного не хватает — остановить анализ

    # Молярные массы (в г/моль) для каждого компонента
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

    Vm = 0.022414  # Молярный объем (м³/моль) при нормальных условиях

    # Расчет содержания каждого компонента в г/м³:
    for comp in components:
        # перевод из % об. в г/м³: (об.% / 100) * молярная масса / молярный объем
        df[comp + "_g_m3"] = df[comp] / 100 * molar_masses[comp] / Vm

    # Суммируем все пересчитанные компоненты, получаем общее содержание С₃+в.
    df["С3+в."] = df[[f"{c}_g_m3" for c in components]].sum(axis=1)

    # ───── Блок статистики ─────
    st.markdown("### 📈 Статистика по С₃+в.")
    col1, col2, col3 = st.columns(3)
    col1.metric("Среднее", f"{df['С3+в.'].mean():.2f} г/м³")
    col2.metric("Максимум", f"{df['С3+в.'].max():.2f} г/м³")
    col3.metric("Минимум", f"{df['С3+в.'].min():.2f} г/м³")

    # ───── График распределения С₃+в. по диапазонам ─────
    st.markdown("### 📊 Распределение по диапазонам С₃+в. (г/м³)")

    # Определение интервалов (бинов) для группировки данных
    bins = [0, 100, 200, 300, 400, 500, 600, 800, 1000, 1300, 1500]
    # Подписи для каждого интервала
    labels = [f"{bins[i]}–{bins[i+1]}" for i in range(len(bins) - 1)]

    # Категоризация значений по интервалам
    df["С3+в._range"] = pd.cut(df["С3+в."], bins=bins, labels=labels, include_lowest=True)

    # Подсчет количества записей в каждом диапазоне
    s3plus_counts = df["С3+в._range"].value_counts().sort_index()
    s3plus_counts = s3plus_counts[s3plus_counts > 0]  # Убираем диапазоны с 0 значениями

    # Построение горизонтальной гистограммы
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(s3plus_counts.index.astype(str), s3plus_counts.values, color='orange')
    ax.set_xlabel("Количество отборов")
    ax.set_ylabel("Диапазон С₃+в., г/м³")
    ax.set_title("Распределение С₃+в. по диапазонам")

    # Подписи на гистограмме
    for i, v in enumerate(s3plus_counts.values):
        ax.text(v + 0.5, i, str(v), va='center', fontsize=9)

    # Отображаем график в Streamlit
    st.pyplot(fig)

    # ───── Вывод таблицы с результатами ─────
    # Выбираем доступные метаданные для отображения
    display_cols = [col for col in ["Месторождение", "ДНС", "Ступень отбора", "Дата протокола"] if col in df.columns]

    # Создаем финальный датафрейм для отображения
    df_display = df[display_cols + components + ["С3+в."]].copy()
    df_display["С3+в."] = df_display["С3+в."].round(2)  # округляем результат

    # CSS-стили для таблицы (лучшее форматирование)
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

    # Отображаем HTML-таблицу в блоке с пользовательскими стилями
    st.markdown(f'<div class="scroll-free-table">{df_display.to_html(index=False)}</div>', unsafe_allow_html=True)
