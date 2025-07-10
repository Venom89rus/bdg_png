import pandas as pd

# Общая точка соединения
common_point_nsk = [63.300, 75.500]

# Загружаем координаты ветки 1 из Excel
df = pd.read_excel("coords_nsk.xlsx")
path_from_excel = df[["Latitude", "Longitude"]].values.tolist()

# Добавляем точку соединения в конец маршрута
path_from_excel.append(common_point_nsk)

# Обновлённый pipeline_data_nsk
pipeline_data_nsk = [
    {
        "name": "Ветка 1",
        "path": path_from_excel,
        "color": "blue"
    },
    {
        "name": "Ветка 2",
        "path": [
            [63.310, 75.400],
            [63.305, 75.430],
            [63.302, 75.460],
            common_point_nsk
        ],
        "color": "green"
    },
    {
        "name": "Ветка 3",
        "path": [
            [63.280, 75.600],
            [63.290, 75.570],
            [63.295, 75.530],
            common_point_nsk
        ],
        "color": "orange"
    }
]
