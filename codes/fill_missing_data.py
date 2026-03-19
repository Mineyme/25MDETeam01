# -*- coding: utf-8 -*-
"""
数据补全脚本：将爬取的缺失数据填充回原始数据，重新清洗并保存
"""
import pandas as pd
import json
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_RAW = os.path.join(project_root, "data_raw")
DATA_CLEAN = os.path.join(project_root, "data_clean")

# ============================================================
# 1. 读取原始数据
# ============================================================
df_merge_raw = pd.read_csv(os.path.join(DATA_RAW, "merged_raw.csv"))
df_merge_raw['year'] = df_merge_raw['year'].astype(int)
print(f"原始数据: {df_merge_raw.shape}")
print(f"补全前缺失值:\n{df_merge_raw[df_merge_raw['year'] <= 2024].isnull().sum()}")

# ============================================================
# 2. 读取爬取的缺失数据
# ============================================================
with open(os.path.join(DATA_RAW, "missing_data_scraped.json"), 'r', encoding='utf-8') as f:
    missing_data = json.load(f)

print(f"\n待补全数据:")
print(json.dumps(missing_data, ensure_ascii=False, indent=2))

for key, value in missing_data.items():
    city, year_str = key.rsplit("_", 1)
    year = int(year_str)
    mask = (df_merge_raw['city'] == city) & (df_merge_raw['year'] == year)
    if mask.any():
        for col, val in value.items():
            df_merge_raw.loc[mask, col] = val
    else:
        print(f"警告：未找到 {city} {year} 的记录，请检查原数据。")

# 验证
print(f"\n补全后缺失值:\n{df_merge_raw.isnull().sum()}")
print(f"\n数据维度: {df_merge_raw.shape}")

# ============================================================
# 5. 保存补全后的原始数据
# ============================================================
df_merge_raw.to_csv(os.path.join(DATA_RAW, "merged_raw.csv"), index=False, encoding="utf-8-sig")
print(f"\n补全后原始数据已保存: merged_raw.csv")
