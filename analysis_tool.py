import os
import geopandas as gpd
import pandas as pd
from tqdm import tqdm
from shapely.geometry import Point
from shapely.geometry import box
import matplotlib.pyplot as plt

# region 用于相关性分析
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


def load_all_gdfs(root="origin_data", extensions=None):
    if extensions is None:
        extensions = [".shp", ".geojson"]
    gdf_dict = {}

    for folder in sorted(os.listdir(root)):
        folder_path = os.path.join(root, folder)
        if not os.path.isdir(folder_path):
            continue

        files = [f for f in os.listdir(folder_path) if any(f.endswith(ext) for ext in extensions)]

        if not files:
            print(f"⚠️  {folder} 中没有找到有效矢量文件，跳过")
            continue

        file_path = os.path.join(folder_path, files[0])
        try:
            # 获取文件大小
            file_size_mb = os.path.getsize(file_path) / 1024 / 1024  # 转换为 MB

            gdf = gpd.read_file(file_path).to_crs(epsg=32632)
            if gdf.empty:
                print(f"⚠️  {folder} 的文件为空，跳过")
                continue

            gdf_dict[folder] = gdf
            print(f"✅  已加载 {folder}: {files[0]} ({len(gdf)} 条记录, {file_size_mb:.2f} MB)")
        except Exception as e:
            print(f"❌  加载 {file_path} 时出错：{e}")
            continue

    return gdf_dict


# 统计点类型数量（工厂、公服等）
def count_points_in_grid(gdf_points, grid, column_name):
    print(f" Counting points for {column_name}...")
    tqdm.pandas()

    join = gpd.sjoin(gdf_points, grid, how='left', predicate='within')
    count_series = join.groupby('index_right').size()
    grid[column_name] = grid.index.map(count_series).fillna(0)

    return grid

# 统计线的长度（如道路）
def length_lines_in_grid(gdf_lines, grid, column_name):
    print(f"  Calculating total line length for {column_name}...")
    tqdm.pandas()

    join = gpd.sjoin(gdf_lines, grid, how='left', predicate='intersects')
    join['length'] = join.geometry.length

    length_series = join.groupby('index_right')['length'].sum()
    grid[column_name] = grid.index.map(length_series).fillna(0)

    return grid

# 统计面的面积（如工业、农业、水体）
def area_polygons_in_grid(gdf_polygons, grid, column_name):
    print(f"  Calculating area for {column_name}...")
    # 修复无效几何
    gdf_polygons['geometry'] = gdf_polygons['geometry'].apply(
        lambda geom: geom if geom.is_valid else geom.buffer(0)
    )
    tqdm.pandas()

    join = gpd.sjoin(gdf_polygons, grid, how='left', predicate='intersects')
    # 再修复 join 后可能产生的无效几何
    join['geometry'] = join['geometry'].apply(lambda geom: geom if geom.is_valid else geom.buffer(0))

    join['intersect_area'] = join.progress_apply(
        lambda row: row.geometry.intersection(grid.loc[row['index_right'], 'geometry']).area
        if pd.notnull(row['index_right']) else 0, axis=1
    )

    area_by_grid = join.groupby('index_right')['intersect_area'].sum()
    grid[column_name] = grid.index.map(area_by_grid).fillna(0)

    return grid

# 计算交叉路口数量
def extract_road_intersections(gdf_roads):
    gdf_roads = gdf_roads[gdf_roads.geometry.type.isin(["LineString", "MultiLineString"])].reset_index(drop=True)

    # 使用空间索引查找可能相交的线段组合
    intersections = []

    for i, geom1 in tqdm(gdf_roads.geometry.items(), total=len(gdf_roads), desc="提取交叉口"):
        candidates = gdf_roads.sindex.query(geom1, predicate="intersects")
        for j in candidates:
            if i >= j:
                continue
            geom2 = gdf_roads.geometry.iloc[j]
            inter = geom1.intersection(geom2)
            if inter.is_empty:
                continue
            if inter.geom_type == "Point":
                intersections.append(inter)
            elif inter.geom_type == "MultiPoint":
                intersections.extend([pt for pt in inter.geoms])

    # 构造交叉点 GeoDataFrame 并去重
    gdf_intersections = gpd.GeoDataFrame(geometry=intersections, crs=gdf_roads.crs)
    gdf_intersections = gdf_intersections.drop_duplicates(subset="geometry")

    return gdf_intersections
# endregion


# region 用于聚类
def square_buffer(center, half_size=500):
    x, y = center.x, center.y
    return box(x - half_size, y - half_size, x + half_size, y + half_size)

def render_patch_images(
    building, farming, processing, road, water,
    output_dir="rendered_images", half_size=500, dpi=300
):
    os.makedirs(output_dir, exist_ok=True)

    def render_one_image(center_point, index):
        buffer = square_buffer(center_point, half_size=half_size)
        def clip_layer(gdf): return gdf[gdf.geometry.intersects(buffer)]

        bld_clip = clip_layer(building)
        farm_clip = clip_layer(farming)
        proc_clip = clip_layer(processing)
        road_clip = clip_layer(road)
        water_clip = clip_layer(water)

        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_facecolor("white")

        water_clip.plot(ax=ax, color='blue', edgecolor='none')
        farm_clip.plot(ax=ax, color='green', edgecolor='none')
        road_clip.plot(ax=ax, color='grey', linewidth=5)
        bld_clip.plot(ax=ax, color='black', edgecolor='none')
        proc_clip.plot(ax=ax, color='red')

        ax.set_xlim(buffer.bounds[0], buffer.bounds[2])
        ax.set_ylim(buffer.bounds[1], buffer.bounds[3])
        ax.axis("off")

        plt.tight_layout()
        save_path = os.path.join(output_dir, f"render_{index:03d}.png")
        plt.savefig(save_path, dpi=dpi)
        plt.close()

    for idx, row in processing.iterrows():
        center = row.geometry.centroid
        render_one_image(center, idx)

    print(f"✅ 共生成 {len(processing)} 张图，保存在 {output_dir}/ 中")
# endregion