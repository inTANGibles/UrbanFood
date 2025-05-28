import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import box,Polygon

def calculate_entropy(area_series):
    total = area_series.sum()
    if total == 0:
        return 0
    proportions = area_series / total
    entropy = -np.sum(proportions * np.log(proportions))
    return entropy


gdf_boundary = gpd.read_file(r"G:\IUAV\STUDIO\06_DATA-20250424T073244Z-001\06_DATA\1. Boundaries\Whole area")
gdf_boundary = gdf_boundary.to_crs("EPSG:32632")

# 设置格网大小（单位和你的坐标系一致，比如米）
grid_size = 1000  # 每个正方形边长1000米（1公里）

# 获取工厂数据的包络范围 (bounding box)
minx, miny, maxx, maxy = gdf_boundary.total_bounds

# 创建格网
grid_cells = []
x_left = minx
while x_left < maxx:
    y_bottom = miny
    while y_bottom < maxy:
        cell = box(x_left, y_bottom, x_left + grid_size, y_bottom + grid_size)
        grid_cells.append(cell)
        y_bottom += grid_size
    x_left += grid_size

# 转成GeoDataFrame
grid = gpd.GeoDataFrame({'geometry': grid_cells}, crs="EPSG:32632")
grid["grid_id"] = grid.index.astype(str)
# grid.to_file(r"G:\CODE\data",driver="GeoJSON")


# 加载数据
# grid_gdf = gpd.read_file("grid_1km.geojson")  # 网格图层
landuse_gdf = gpd.read_file(r"G:\CODE\data\05_landuse_mix\landuse_data.shp")  # landuse 图层

# 确保统一投影（UTM zone 32N（单位是米 
grid_gdf = grid.to_crs(epsg=32632)
landuse_gdf = landuse_gdf.to_crs(epsg=32632)

# 保留有效的 landuse 类型
landuse_gdf = landuse_gdf[landuse_gdf["landuse"].notnull()]
# 确保确实存在叫 "landuse" 的字段
# print(landuse_gdf.columns)

# 交集分析：裁剪 landuse 到各个 grid
results = []

for idx, grid in grid_gdf.iterrows():
    grid_geom = grid.geometry
    grid_id = grid["grid_id"]

    # 找到相交的 landuse 面
    intersected = landuse_gdf[landuse_gdf.geometry.intersects(grid_geom)].copy()

    if intersected.empty:
        results.append({"grid_id": grid_id, "entropy": 0})
        continue

    # 裁剪并计算面积
    intersected["geometry"] = intersected.geometry.intersection(grid_geom.buffer(0))
    intersected["area"] = intersected.geometry.area

    # 按 landuse 类型汇总
    grouped = intersected.groupby("landuse")["area"].sum()

    # 计算熵
    entropy = max(0.0, calculate_entropy(grouped))

    results.append({"grid_id": grid_id, "entropy": entropy})

# 转换为 DataFrame 并导出
entropy_df = pd.DataFrame(results)
entropy_gdf = grid_gdf.merge(entropy_df, on="grid_id")
entropy_gdf.to_file(r"G:\CODE\data\05_landuse_mix\grid_entropy.geojson", driver="GeoJSON")