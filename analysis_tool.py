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


