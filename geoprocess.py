import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import os

INPUT_FILE = r'data\ventas_mvdeo_2025-07-13_coords.csv'
df = pd.read_csv(INPUT_FILE)

# --- 1. Data Cleaning ---
# Convert coordinates to numeric
df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
df["lng"] = pd.to_numeric(df["lng"], errors="coerce")

# Drop rows with invalid coordinates
df = df.dropna(subset=["lat", "lng"])

# Handle missing 'metraje' values
df.loc[df.metraje.isna(), 'metraje'] = df.loc[df.metraje.isna(), 'metraje_2']

# Filter and reset index
df = df.loc[df.metraje > 15].copy()  # Use .copy() to avoid SettingWithCopyWarning
df.reset_index(drop=True, inplace=True)  # Cleaner index reset

# Calculate valor_metro
df['valor_metro'] = df.valor / df.metraje

# --- 2. Create Point GeoDataFrame ---
geometry = [Point(lng, lat) for lng, lat in zip(df["lng"], df["lat"])]
pts = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")
pts = pts.to_crs("EPSG:32721")

# --- 3. Save Points ---
output_dir = "data"
os.makedirs(output_dir, exist_ok=True)
output_gpkg = os.path.join(output_dir, "points_2025-07-13.gpkg")
pts.to_file(output_gpkg, driver="GPKG")
print(f"GeoPackage saved to: {output_gpkg}")

# --- 4. Spatial Join with Grid ---
grid_path = r'capas\grilla_hex.gpkg'
grid = gpd.read_file(grid_path)

# Ensure grid is in same CRS as points
grid = grid.to_crs("EPSG:32721")

# Perform spatial join
pegue = gpd.sjoin(
    pts,
    grid,
    how="inner",
    predicate="within"
)

# Save joined data
pegue.to_file(r'capas\pegue_test.gpkg', driver="GPKG")

# --- 5. Calculate Median Values ---
# Group by grid cell and calculate median
agru = pegue.groupby('id')['valor_metro'].median().reset_index()

# Merge with original grid
data_grid = grid.merge(
    agru,
    on='id', 
    how='inner'
)

# Select and rename columns
data_grid = data_grid[['id', 'valor_metro', 'geometry']]  # Use 'id' instead of 'index_right'
data_grid = data_grid.rename(columns={'id': 'grid_id'})
data_grid['valor_metro'] = data_grid['valor_metro'].round().astype(int)

# Save final grid
fecha = '2025-07-13'
data_grid.to_file(f'capas/grid_median_{fecha}.gpkg', driver="GPKG")


grid_webmap = data_grid.loc[:, ['valor_metro', 'geometry']].copy()
grid_webmap = grid_webmap.to_crs("EPSG:4326")
grid_webmap.rename(columns={'valor_metro': 'median_price'}, inplace=True)
file_path = f'capas/hexgrid_{fecha}.js'
grid_webmap.to_file(file_path, driver="GeoJSON")

# prepend var name
text_to_prepend = 'var hexgrid = '

with open(file_path, 'r') as file:
    original_content = file.read()

with open(file_path, 'w') as file:
    file.write(text_to_prepend + original_content)

print(f"Added '{text_to_prepend}' to {file_path}")
