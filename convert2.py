import pandas as pd
import re
from pyproj import Transformer

# 初始化坐标转换器（WGS-84 → UTM Zone 32N）
transformer = Transformer.from_crs("epsg:4326", "epsg:32632", always_xy=True)

# 坐标转换函数（输入为 POINT (lat,lon) 或 POINT (lon,lat) 格式）
def convert_geometry(geom):
    try:
        geom_str = str(geom)
        # 匹配 POINT (lat,lon) 或 POINT (lon,lat)
        match = re.match(r"POINT\s*\(\s*(-?\d+(?:\.\d+)?)\s*,?\s*(-?\d+(?:\.\d+)?)\s*\)", geom_str)
        if match:
            lat = float(match.group(1))
            lon = float(match.group(2))
            x, y = transformer.transform(lon, lat)  # 注意顺序：lon, lat
            return f"POINT ({x:.3f} {y:.3f})"
    except Exception:
        pass
    return None

# 读取表格（支持 .csv 或 .xlsx）
# 示例读取 Excel 文件
df = pd.read_excel(r"G:\CODE\UrbanFood\0528_check_Factory_converted.xlsx")

# 应用转换函数
df['geometry_utm32n'] = df['geometry'].apply(convert_geometry)

# 保存结果为新的 Excel 文件
df.to_excel(r"G:\CODE\UrbanFood\0529_check_Factory_converted.xlsx", index=False)

# 打印前几行结果验证
print(df[['geometry', 'geometry_utm32n']].head())
