import streamlit as st
import folium
from streamlit_folium import st_folium
from folium import Element
from geopy.distance import geodesic

st.set_page_config(layout="wide")
st.title("Схема трубопроводов с точкой соединения и фильтрацией")

# Общая точка соединения
common_point = [63.300, 75.500]

# Названия веток, координаты и цвета
pipeline_data = [
    {"name": "Ветка 1", "start": [63.250, 75.450], "color": "blue"},
    {"name": "Ветка 2", "start": [63.310, 75.400], "color": "green"},
    {"name": "Ветка 3", "start": [63.280, 75.600], "color": "orange"},
]

# Мультивыбор фильтра
all_names = [pipe["name"] for pipe in pipeline_data]
selected_names = st.multiselect("Выберите отображаемые ветки", all_names, default=all_names)

# Фильтруем только выбранные ветки
selected_pipelines = [pipe for pipe in pipeline_data if pipe["name"] in selected_names]

# Расчёт протяжённости
def calculate_total_length_km(pipes):
    return round(sum(geodesic(pipe["start"], common_point).km for pipe in pipes), 2)

total_length = calculate_total_length_km(selected_pipelines)
st.markdown(f"**Протяжённость выбранных веток:** {total_length} км")

# Создание карты
m = folium.Map(
    location=common_point,
    zoom_start=10,
    tiles=None,
    control_scale=True
)

# Чистый фон без флага
folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    attr=' ',
    name='Чистая карта',
    control=False
).add_to(m)

# Добавление выбранных веток
for pipe in selected_pipelines:
    folium.PolyLine(
        locations=[pipe["start"], common_point],
        color=pipe["color"],
        weight=5,
        opacity=0.8,
        tooltip=pipe["name"]
    ).add_to(m)

    folium.Marker(
        location=pipe["start"],
        tooltip=f"Начало: {pipe['name']}",
        icon=folium.Icon(color=pipe["color"])
    ).add_to(m)

# Маркер в точке соединения
folium.Marker(
    location=common_point,
    tooltip="Узел соединения",
    icon=folium.Icon(color="red", icon="glyphicon glyphicon-map-marker")
).add_to(m)

# CSS для скрытия флага/атрибуции
css_hide = Element("""
    <style>
    .leaflet-control-attribution {
        display: none !important;
    }
    </style>
""")
m.get_root().html.add_child(css_hide)

# Отображение карты
st_folium(m, width=1200, height=700)
