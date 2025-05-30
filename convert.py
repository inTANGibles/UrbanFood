import pandas as pd
import re
from pyproj import Transformer

# 初始化坐标转换器（EPSG:32632 → EPSG:4326）
transformer = Transformer.from_crs("epsg:32632", "epsg:4326", always_xy=True)

# 坐标转换函数
def convert_geometry(geom):
    try:
        geom_str = str(geom)
        match = re.match(r"POINT\s*\(\s*(-?\d+(?:\.\d+)?)\s+(-?\d+(?:\.\d+)?)\s*\)", geom_str)
        if match:
            x = float(match.group(1))
            y = float(match.group(2))
            lon, lat = transformer.transform(x, y)
            # 保留小数点后 7 位，按纬度在前、经度在后的格式输出
            return f"POINT ({lat:.7f},{lon:.7f})"
    except Exception:
        pass
    return None

# 读取 CSV 文件
df = pd.read_csv(r"G:\CODE\0518\01Factory.csv")

# 应用转换函数并生成新的 geometry 列
df['geometry_wgs84'] = df['geometry'].apply(convert_geometry)

# 可选：输出新 CSV 文件
df.to_csv(r"G:\CODE\0518\01Factory_converted.csv", index=False)

# 打印前几行结果
print(df[['geometry', 'geometry_wgs84']].head())
