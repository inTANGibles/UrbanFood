import os
import geopandas as gpd
def get_folder_sizes(root="origin_data"): # 用以检测是否可以上传 GIT-HUB
    """
    返回 root 下每个子文件夹的大小（单位：MB），并按大小降序排序。
    """
    folder_sizes = []

    for folder in os.listdir(root):
        folder_path = os.path.join(root, folder)
        if os.path.isdir(folder_path):
            total_size = 0
            for dirpath, _, filenames in os.walk(folder_path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total_size += os.path.getsize(fp)
            folder_sizes.append((folder, round(total_size / 1024 / 1024, 2)))  # MB

    # 按大小降序排序并打印
    folder_sizes.sort(key=lambda x: x[1], reverse=True)

    print("📦 子文件夹占用大小（单位：MB）")
    for name, size in folder_sizes:
        print(f"{name:30} {size:>8} MB")

    return folder_sizes


def load_all_gdfs(root="origin_data",  extensions=None):
    """
    批量读取 origin_data 下的所有子文件夹中第一个矢量数据文件（shp 或 geojson）。
    返回：包含多个 GeoDataFrame 的字典，键为文件夹名。
    """

    if extensions is None:
        extensions = [".shp", ".geojson"]
    gdf_dict = {}

    for folder in sorted(os.listdir(root)):
        folder_path = os.path.join(root, folder)
        if not os.path.isdir(folder_path):
            continue

        # 搜索支持的矢量文件类型
        files = [f for f in os.listdir(folder_path) if any(f.endswith(ext) for ext in extensions)]

        if not files:
            print(f"⚠️  {folder} 中没有找到有效矢量文件，跳过")
            continue

        file_path = os.path.join(folder_path, files[0])
        try:
            gdf = gpd.read_file(file_path).to_crs(epsg=32632)
            if gdf.empty:
                print(f"⚠️  {folder} 的文件为空，跳过")
                continue
            gdf_dict[folder] = gdf
            print(f"✅  已加载 {folder}: {files[0]} ({len(gdf)} 条记录)")
        except Exception as e:
            print(f"❌  加载 {file_path} 时出错：{e}")
            continue

    return gdf_dict


# 统计点类型数量（工厂、公服等）
def count_points_in_grid(gdf_points, grid, column_name):
    join = gpd.sjoin(gdf_points, grid, how='left', predicate='within')
    grid[column_name] = join.groupby('index_right').size()
    grid[column_name] = grid[column_name].fillna(0)
    return grid

# 统计线的长度（如道路）
def length_lines_in_grid(gdf_lines, grid, column_name):
    join = gpd.sjoin(gdf_lines, grid, how='left', predicate='intersects')
    join['length'] = join.geometry.length
    grid[column_name] = join.groupby('index_right')['length'].sum()
    grid[column_name] = grid[column_name].fillna(0)
    return grid

# 统计面的面积（如工业、农业、水体）
def area_polygons_in_grid(gdf_polygons, grid, column_name):
    join = gpd.sjoin(gdf_polygons, grid, how='left', predicate='intersects')
    join['intersect_area'] = join.geometry.intersection(join['geometry']).area
    area_by_grid = join.groupby('index_right')['intersect_area'].sum()
    grid[column_name] = grid.index.map(area_by_grid).fillna(0)
    return grid