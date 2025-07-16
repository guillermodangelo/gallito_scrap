import pandas as pd
import numpy as np
import pickle
import time
from concurrent.futures import ThreadPoolExecutor
from scraper_gallito import scrap_latlng

DEBUG = False
THREADS = 6
INPUT_FILE = r'data\ventas_mvdeo_2025-07-13.csv'

if DEBUG:
    THREADS = 2

try:
    if DEBUG:
        data = pd.read_csv(INPUT_FILE).head(400)
    else:
        data = pd.read_csv(INPUT_FILE)
    print(f'Loaded file: {INPUT_FILE}, with {len(data)} rows.')
    data.head()
except Exception as e:
    print(f'Error loading file.')
    raise e

urls = np.array_split(list(data.url.values), THREADS)
all_results = []

start = time.time()

with ThreadPoolExecutor(THREADS) as executor:
    for result in executor.map(scrap_latlng, urls):
        all_results.append(result)

end = time.time()
print(f'Scrapping finished in {end - start} seconds.')

all_results_plain = [(coord, dist) for tuple_pair in all_results for coord, dist in zip(*tuple_pair)]

print(f'Number of coords: {len(all_results_plain)}')

with open('data/temp.pkl','wb') as f:
    pickle.dump(all_results_plain, f)