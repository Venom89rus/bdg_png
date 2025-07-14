import pandas as pd

# Загружаем таблицу
df = pd.read_excel("pipe.xlsx", sheet_name="ХКЦ", skiprows=2)

# Названия маршрутов (шапка таблицы, шаг 2 колонки)
column_names = df.columns
route_names = [column_names[i] for i in range(0, len(column_names), 2)]

# Преобразуем в pipeline_data
pipeline_data = []
colors = ["blue", "green", "orange", "purple", "gray", "black", "red"]

for idx, name in enumerate(route_names):
    lat_col = column_names[idx * 2]
    lon_col = column_names[idx * 2 + 1]
    coords = df[[lat_col, lon_col]].dropna()
    path = list(zip(coords[lat_col], coords[lon_col]))

    if path:
        pipeline_data.append({
            "name": name,
            "path": path,
            "color": colors[idx % len(colors)]
        })

# Общая точка соединения = конец последнего маршрута
common_point = pipeline_data[-1]["path"][-1]

# Сохраняем в файл
with open("noyabrsk_region.py", "w", encoding="utf-8") as f:
    f.write("pipeline_data = " + repr(pipeline_data) + "\n")
    f.write("common_point = " + repr(common_point) + "\n")
