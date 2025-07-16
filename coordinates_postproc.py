import pickle
import pandas as pd
import numpy as np
from datetime import datetime

INPUT_FILE = r'data\ventas_mvdeo_2025-07-13.csv'

def save(input_data, fecha = None):
    if fecha is None:
        fecha_str = str(datetime.today().date())
    else:
        fecha_str = fecha
    filename = f'data/ventas_mvdeo_{fecha_str}_coords.csv'
    input_data.to_csv(filename, index=False)


def parse_coordinates(coord_str):
    try:
        if ',' in coord_str and '.' in coord_str:
            lat, lon = coord_str.split(',')
        elif coord_str == 'Nan,Nan' or coord_str == '0,0':
            lat, lon = [np.nan, np.nan]
        else:
            parts = coord_str.split(',')
            lat = f"{parts[0]}.{parts[1]}"
            lon = f"{parts[2]}.{parts[3]}"
    except Exception as e:
        lat, lon = [np.nan, np.nan]
        print(f'Error parsing coordinates: {coord_str}')
        print(e)

    return np.round(float(lat), 5), np.round(float(lon), 5)


try:
    data = pd.read_csv(INPUT_FILE)
    print(f'Loaded file: {INPUT_FILE}, with {len(data)} rows.')
except Exception as e:
    print(f'Error loading file.')
    raise e

with open(r"data\temp.pkl", "rb") as f:     
    all_results_plain = pickle.load(f)

print(len(all_results_plain))


# recuperas los metrajes
metraje = [i[1] for i in all_results_plain]
data['metraje_2'] = metraje
data['metraje_2'] = data['metraje_2'].str.replace(r'\D', '', regex=True)
data['metraje_2'] = data['metraje_2'].str.strip()
data.loc[data['metraje_2'] == '', 'metraje_2'] = np.nan
data['metraje_2'] = data['metraje_2'].astype(float)
print('Metraje de las ventas')
print(data.metraje_2.describe())


# recupera coordenadas
coords = [i[0] for i in all_results_plain]
coords_splitted = [parse_coordinates(i) for i in coords]
data[['lat', 'lng']] = coords_splitted

print(data.head())


save(data, '2025-07-13')