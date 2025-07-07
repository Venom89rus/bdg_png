import streamlit as st
from streamlit_option_menu import option_menu
import matplotlib
matplotlib.use('Agg')
import base64

# Настройки страницы
st.set_page_config(page_title="Аналитика газа", page_icon="🛠", layout="wide")

# Функция для кодирования изображения в base64
def get_image_as_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

logo_base64 = get_image_as_base64("img/logo.png")

with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{logo_base64}" width="100">
        </div>
        """,
        unsafe_allow_html=True
    )
    selected = option_menu(
        menu_title="Навигация",
        options=["Главная", "Аналитика", "Гидравлика", "Метанол", "Отчеты", "Контакты"],
        icons=["house", "bar-chart", "diagram-3", "moisture", "printer", "envelope-at"],
        menu_icon="cast",
        default_index=0,
        styles={
            "container": {"padding": "5!important", "background-color": "#f0f2f6"},
            "icon": {"color": "blue", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "left", "margin": "5px", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#0284c7", "color": "white"},
        }
    )

if selected == "Главная":
    st.title("Добро пожаловать Газовичёк 👋")
    st.write("Это дашборд по анализу гидравлических потерь, потреблению метанола, компонентному составу газа.")
    st.markdown("## 🔍 Возможности:")
    st.markdown("- Визуализация состава газа\n- Генерация отчётов\n- Фильтрация по локациям")

elif selected == "Аналитика":
    import analitika
    analitika.run_analytics()

elif selected == "Гидравлика":
    st.title("💻 Гидравлические расчеты")
    import gidravlika
    gidravlika.run_hydraulic_calc()

elif selected == "Метанол":
    import methanol
    methanol.run_methanol_calc()

elif selected == "Отчеты":
    st.title("✅ Отчеты")
    st.markdown("Выберите параметры и скачайте PDF/Excel.")

elif selected == "Контакты":
    st.title("📰 Контакты")
    st.markdown("""
        Разработчики:  
        Роман Зинченко, Email: yourname@company.com  
        Юрий Кудряшов, Email: yourname@company.com
    """, unsafe_allow_html=True)
