import streamlit as st
import pydeck as pdk
import pandas as pd

st.title("🗺️ Газопровод на карте")

# Координаты начала и конца (широта, долгота)
point_A = [65.0, 76.0]       # Начало
point_B = [65.045, 76.07]    # Конец (примерно 5 км по прямой)

# DataFrame с координатами линии
pipeline_df = pd.DataFrame({
    "lat": [point_A[0], point_B[0]],
    "lon": [point_A[1], point_B[1]]
})

# Слой для линии трубопровода
line_layer = pdk.Layer(
    "LineLayer",
    data=pipeline_df,
    get_source_position="[lon[0], lat[0]]",
    get_target_position="[lon[1], lat[1]]",
    get_color=[255, 140, 0],  # Оранжевая линия
    get_width=5,
    pickable=True,
    auto_highlight=True
)

# Центр карты
midpoint = [(point_A[0] + point_B[0]) / 2, (point_A[1] + point_B[1]) / 2]

# Отображение карты
st.pydeck_chart(pdk.Deck(
    initial_view_state=pdk.ViewState(
        latitude=midpoint[0],
        longitude=midpoint[1],
        zoom=10,
        pitch=30,
    ),
    layers=[line_layer],
    tooltip={"text": "Газопровод от точки A до B"}
))
