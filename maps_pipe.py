import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium import Element
from geopy.distance import geodesic

st.set_page_config(layout="wide")
st.title("Схема трубопроводов с точкой соединения и фильтрацией")

# ===== Загрузка данных =====
uploaded_file = "pipe.xlsx"  # Путь к файлу
sheet_options = ["ХКЦ", "МГПЗ", "ВГПЗ", "ВяКЦ", "ОГМ", "ВТГМ"]

selected_sheet = st.selectbox("Выберите участок (вкладку):", sheet_options)

@st.cache_data
def load_pipeline_data(sheet_name):
    df = pd.read_excel(uploaded_file, sheet_name=sheet_name, skiprows=2)
    columns = df.columns
    route_names = [columns[i] for i in range(0, len(columns), 2)]

    colors = ["blue", "green", "orange", "purple", "gray", "black", "red"]

    pipeline_data = []

    for idx, name in enumerate(route_names):
        lat_col = columns[idx * 2]
        lon_col = columns[idx * 2 + 1]

        coords = df[[lat_col, lon_col]].dropna()
        path = list(zip(coords[lat_col], coords[lon_col]))

        if path:
            pipeline_data.append({
                "name": name,
                "path": path,
                "start": path[0],
                "color": colors[idx % len(colors)]
            })

    # Общая точка соединения — конец последнего маршрута
    common_point = pipeline_data[-1]["path"][-1] if pipeline_data else [63.300, 75.500]
    return pipeline_data, common_point

pipeline_data, common_point = load_pipeline_data(selected_sheet)

# ===== Интерфейс фильтрации =====
all_names = [pipe["name"] for pipe in pipeline_data]
selected_names = st.multiselect("Выберите отображаемые ветки", all_names, default=all_names)
selected_pipelines = [pipe for pipe in pipeline_data if pipe["name"] in selected_names]

# ===== Расчёт протяжённости =====
def calculate_length(path):
    return sum(geodesic(path[i], path[i + 1]).km for i in range(len(path) - 1))

total_length = round(sum(calculate_length(pipe["path"]) for pipe in selected_pipelines), 2)
st.markdown(f"**Протяжённость выбранных веток:** {total_length} км")

# ===== Создание карты =====
m = folium.Map(location=common_point, zoom_start=10, tiles=None, control_scale=True)

folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
    attr=' ',
    name='Чистая карта',
    control=False
).add_to(m)

for pipe in selected_pipelines:
    folium.PolyLine(
        locations=pipe["path"],
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

# Узел соединения
folium.Marker(
    location=common_point,
    tooltip="Узел соединения",
    icon=folium.Icon(color="red", icon="glyphicon glyphicon-map-marker")
).add_to(m)

css_hide = Element("""
    <style>
    .leaflet-control-attribution {
        display: none !important;
    }
    </style>
""")
m.get_root().html.add_child(css_hide)

# ===== Отображение карты =====
st_folium(m, width=1200, height=700)
