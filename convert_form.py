import pandas as pd
import geopandas as gpd
from shapely.wkt import loads

# === 1. 读取 Excel 文件 ===
input_excel_path = r"G:\CODE\UrbanFood\0529_check_Factory_converted.xlsx"
df = pd.read_excel(input_excel_path)

# === 2. 清洗并解析 geometry 列（WKT 格式） ===
df = df[df['geometry'].apply(lambda x: isinstance(x, str))].copy()
df['geometry'] = df['geometry'].apply(loads)

# === 3. 创建 GeoDataFrame，设置为 EPSG:32632（UTM Zone 32N） ===
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:32632')

# === 4. 导出为 Shapefile ===
output_shapefile_path = r"G:\CODE\UrbanFood\origin_data\04_transformation_industry\processing.shp"
gdf.to_file(output_shapefile_path, driver='ESRI Shapefile')

# === 5. 同步导出为 CSV ===
output_csv_path = r"G:\CODE\UrbanFood\origin_data\04_transformation_industry\processing.csv"
gdf.to_csv(output_csv_path, index=False)

print("✅ 已成功导出为 Shapefile：", output_shapefile_path)
print("✅ 同步导出为 CSV 文件：", output_csv_path)
