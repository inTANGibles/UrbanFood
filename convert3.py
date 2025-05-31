import pandas as pd
import geopandas as gpd
from shapely.wkt import loads

# 读取最新上传的文件
file_path = r"G:\CODE\UrbanFood\0530processing_data.xlsx"
df = pd.read_excel(file_path)

# 过滤出合法的 WKT 字符串
df = df[df['geometry'].apply(lambda x: isinstance(x, str))].copy()

# 保留原始 WKT 列
df['geometry_32632'] = df['geometry']

# 将 WKT 转为 Shapely 几何对象
df['geometry'] = df['geometry'].apply(loads)

# 创建 GeoDataFrame，原始坐标系为 EPSG:32632
gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:32632')

# 转换为 EPSG:3857 坐标系
gdf_3857 = gdf.to_crs(epsg=3857)

# 添加转换后 WKT 列
gdf_3857['geometry_3857'] = gdf_3857['geometry'].apply(lambda geom: geom.wkt)

# 删除当前 active geometry 列，只保留原始与转换后两列
gdf_3857 = gdf_3857.drop(columns=['geometry'])

# 输出为新的 Excel 文件
output_path = r"G:\CODE\UrbanFood\02_0530processing_data.xlsx"
gdf_3857.to_excel(output_path, index=False)

output_path
