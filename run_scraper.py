import numpy as np
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from scraper_gallito import scraper

THREADS = 8
DEBUG = False
DRIVER_PATH = r"C:\chromedriver.exe"
BASE_URL = 'https://www.gallito.com.uy/inmuebles/casas/venta/montevideo/ord_asc?pag='


def clean(input_data):
    data = input_data.copy()
    data['valor'].str.replace('U', '')

    for word, rep in {"U":" ", "S":"", "$":"", ".":""}.items():
        data['valor'] = data['valor'].str.replace(word, rep, regex=False)

    data['valor'] = data['valor'].astype(int)

    print('Valor de las ventas')
    print(data.valor.describe())

    # elimina outliers en valor
    data = data.loc[~((data.valor == 111111111) | (data.valor < 30000))]

    # depura campo metraje
    data['metraje'] = data['metraje'].str.strip()
    data.loc[data['metraje'] == '', 'metraje'] = np.nan

    data['metraje'] = data['metraje'].astype(float)
    print('Metraje de las ventas')
    print(data.metraje.describe())

    return data


def save(input_data):
    fecha_str = str(datetime.today().date())
    filename = f'data/ventas_mvdeo_{fecha_str}.csv'
    input_data.to_csv(filename, index=False)


all_urls = [BASE_URL + str(page) for page in range(1, 200)]

if DEBUG:
    all_urls = all_urls[:8]

urls = np.array_split(all_urls, THREADS)

all_results = []

with ThreadPoolExecutor(THREADS) as executor:
    for result in executor.map(scraper, urls):
        all_results.append(result)


raw_data = pd.concat(all_results).reset_index(drop=True)

print(raw_data.head())

clean_data = clean(raw_data)
save(clean_data)