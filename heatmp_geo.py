import json
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import shape
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'

# Load the CSV data with predicted cases
csv_path = 'predicted_cases_2024-01-01.csv'
data = pd.read_csv(csv_path, encoding='euc-kr')

# Load the Seoul district boundaries JSON data
json_path = 'TL_SCCO_SIG.json'
with open(json_path, encoding='utf-8') as f:
    geo_data = json.load(f)

# Create a GeoDataFrame from the JSON data, filtering for Seoul districts
districts = []
for feature in geo_data['features']:
    if feature['properties']['SIG_CD'].startswith("11"):  # Filter only Seoul districts
        district_name = feature['properties']['SIG_KOR_NM']
        geometry = shape(feature['geometry'])
        districts.append({'district': district_name, 'geometry': geometry})

gdf = gpd.GeoDataFrame(districts, crs="EPSG:4326")

# Merge the CSV data with the GeoDataFrame
data = data.rename(columns={'district': 'district'})  # Ensure column names match
merged_gdf = gdf.merge(data, on='district', how='left')

# Normalize the case values for color intensity
norm = Normalize(vmin=merged_gdf['LSTM'].min(), vmax=merged_gdf['LSTM'].max())
cmap = plt.cm.Reds  # Red color map for intensity

# Plotting
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
merged_gdf.boundary.plot(ax=ax, linewidth=1)
merged_gdf.plot(column='LSTM', cmap=cmap, linewidth=0.8, ax=ax, edgecolor='black', legend=False)

# Adding district names at the center of each district with custom adjustments
for idx, row in merged_gdf.iterrows():
    if not pd.isna(row['LSTM']):  # Only add name if data is available
        centroid = row['geometry'].centroid
        
        # Adjust the position for specific districts
        x_offset = 0
        y_offset = 0
        
        if row['district'] == '서초구':
            x_offset = -0.008  # Move slightly to the left
        elif row['district'] == '종로구':
            x_offset = -0.0025
            y_offset = -0.008  # Move slightly down
        elif row['district'] == '강북구':
            x_offset = -0.0035
            y_offset = -0.005  # Move slightly down
        elif row['district'] == '성북구':
            y_offset = -0.005 
        elif row['district'] == '도봉구':
            y_offset = -0.004
        elif row['district'] == '동대문구':
            y_offset = -0.004
        elif row['district'] == '중랑구':
            y_offset = -0.004
        elif row['district'] == '서대문구':
            y_offset = -0.005
        elif row['district'] == '은평구':
            x_offset = 0.0035
        elif row['district'] == '마포구':
            y_offset = -0.004
        elif row['district'] == '광진구':
            x_offset = 0.002
        elif row['district'] == '양천구':
            y_offset = -0.0035
        elif row['district'] == '영등포구':
            x_offset = 0.0035
        elif row['district'] == '구로구':
            y_offset = 0.0035
        elif row['district'] == '강남구':
            x_offset = -0.007
            y_offset = -0.002
        elif row['district'] == '서초구':
            y_offset = 0.007

        plt.text(
            centroid.x + x_offset, centroid.y + y_offset, row['district'],
            ha='center', va='center',  # Center alignment
            fontsize=10,               # Font size
            fontweight='bold',         # Font weight
            fontname='Malgun Gothic',  # Font family for Korean text
            color='black'              # Font color
        )

# Adding a color bar for reference
sm = ScalarMappable(cmap=cmap, norm=norm)
sm.set_array([])
cbar = fig.colorbar(sm, ax=ax, shrink=0.5)

plt.axis('off')  # Hide axis
plt.show()
