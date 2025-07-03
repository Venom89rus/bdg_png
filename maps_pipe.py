import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic

# Пример координат трубопровода
pipeline_coords = [
    [63.201, 75.450],
    [63.250, 75.500],
    [63.300, 75.550],
    [63.350, 75.600],
]

# Расчёт длины
def calculate_length_km(coords):
    total_length = 0.0
    for i in range(1, len(coords)):
        total_length += geodesic(coords[i - 1], coords[i]).km
    return round(total_length, 2)

st.title("Визуализация трубопровода")
length_km = calculate_length_km(pipeline_coords)
st.markdown(f"**Протяжённость трубопровода:** {length_km} км")

# Создание карты
m = folium.Map(
    location=pipeline_coords[0],
    zoom_start=9,
    tiles=None,
    control_scale=True
)

# Добавление слоя без логотипа и надписей
folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    attr='.',  # <- точка как "заглушка" для атрибуции
    name='Без логотипа',
    control=False
).add_to(m)

# Линия трубопровода
folium.PolyLine(
    locations=pipeline_coords,
    color="blue",
    weight=5,
    opacity=0.8,
    tooltip="Трубопровод"
).add_to(m)

# Метки
folium.Marker(pipeline_coords[0], tooltip="Начало", icon=folium.Icon(color="green")).add_to(m)
folium.Marker(pipeline_coords[-1], tooltip="Конец", icon=folium.Icon(color="red")).add_to(m)

# Отображение в Streamlit
st_folium(m, width=1000, height=600)
