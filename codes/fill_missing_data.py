# -*- coding: utf-8 -*-
"""
数据补全脚本：将爬取的缺失数据填充回原始数据，重新清洗并保存
"""
import pandas as pd
import numpy as np
import json
import os

DATA_RAW = r"D:\Project\City_Budget_Analysis\data_raw"
DATA_CLEAN = r"D:\Project\City_Budget_Analysis\data_clean"

# ============================================================
# 1. 读取原始数据
# ============================================================
df = pd.read_csv(os.path.join(DATA_RAW, "merged_raw.csv"))
df['year'] = df['year'].astype(int)
print(f"原始数据: {df.shape}")
print(f"补全前缺失值:\n{df[df['year']<=2024].isnull().sum()}")

# ============================================================
# 2. 读取爬取的缺失数据
# ============================================================
with open(os.path.join(DATA_RAW, "missing_data_scraped.json"), 'r', encoding='utf-8') as f:
    missing_data = json.load(f)

print(f"\n待补全数据:")
print(json.dumps(missing_data, ensure_ascii=False, indent=2))

# ============================================================
# 3. 填充缺失数据
# ============================================================
fill_map = {
    ('哈尔滨', 2022): {'income': 262.2, 'expend': 1065.5},
    ('昆明', 2009): {'income': 201.61, 'expend': 270.45, 'deposit': 1922.92},
    ('拉萨', 2006): {'gdp': 102.39, 'deposit': 78.99},
    ('拉萨', 2010): {'gdp': 178.91, 'deposit': 151.03},
    ('拉萨', 2012): {'deposit': 223.83},
    ('拉萨', 2013): {'deposit': 272.12},
}

for (city, year), values in fill_map.items():
    mask = (df['city'] == city) & (df['year'] == year)
    if mask.sum() == 0:
        print(f"  WARNING: {city} {year}年 不在数据中!")
        continue
    for col, val in values.items():
        old_val = df.loc[mask, col].values[0]
        df.loc[mask, col] = val
        print(f"  {city} {year}年 {col}: {old_val} -> {val}")

# ============================================================
# 4. 删除2025年空白数据
# ============================================================
df = df[df['year'] <= 2024].copy()

# 验证
print(f"\n补全后缺失值:\n{df.isnull().sum()}")
print(f"\n数据维度: {df.shape}")

# ============================================================
# 5. 保存补全后的原始数据
# ============================================================
df.to_csv(os.path.join(DATA_RAW, "merged_raw_filled.csv"), index=False, encoding="utf-8-sig")
print(f"\n补全后原始数据已保存: merged_raw_filled.csv")

# ============================================================
# 6. 重新执行数据清洗
# ============================================================
print("\n" + "="*60)
print("重新执行数据清洗...")
print("="*60)

# 删除核心指标全为空的行
df = df.dropna(subset=['income', 'expend', 'gdp'], how='all').copy()

# 计算预算缺口
df['gap'] = df['expend'] - df['income']
df['gap_to_gdp'] = df['gap'] / df['gdp']

# 计算增长率
df = df.sort_values(['city', 'year']).reset_index(drop=True)
for col in ['income', 'expend']:
    df[f'{col}_growth'] = df.groupby('city')[col].pct_change() * 100

# 城市分组
tier1 = ['北京', '上海', '广州', '深圳']
pearl_river = ['广州', '深圳']
yangtze_river = ['上海', '南京', '杭州', '宁波', '合肥']

def assign_group(city):
    if city in pearl_river:
        return '珠三角'
    elif city in yangtze_river:
        return '长三角'
    else:
        return '其他'

df['region_group'] = df['city'].apply(assign_group)
df['is_tier1'] = df['city'].isin(tier1)

# 保存清洗后数据
df.to_csv(os.path.join(DATA_CLEAN, "city_budget_clean.csv"), index=False, encoding="utf-8-sig")
print(f"清洗后数据已保存: city_budget_clean.csv ({df.shape})")

# 房地产数据
df_re = pd.read_csv(os.path.join(DATA_RAW, "real_estate_raw.csv"))
df_re['year'] = df_re['year'].astype(int)
df_re = df_re[df_re['year'] <= 2024].copy()
df_re.columns = ['city', 'year', 're_invest', 'sale_area', 're_avg_price', 'res_sale_area', 'res_avg_price']
df_re.to_csv(os.path.join(DATA_CLEAN, "real_estate_clean.csv"), index=False, encoding="utf-8-sig")

# 合并
df_all = df.merge(df_re, on=['city', 'year'], how='left')
df_all.to_csv(os.path.join(DATA_CLEAN, "city_all_clean.csv"), index=False, encoding="utf-8-sig")
print(f"合并数据已保存: city_all_clean.csv ({df_all.shape})")

# ============================================================
# 7. 验证补全效果
# ============================================================
print("\n" + "="*60)
print("验证补全效果")
print("="*60)
print(f"\n最终缺失值:")
print(df.isnull().sum())

# 验证关键数据点
for (city, year), values in fill_map.items():
    row = df[(df['city'] == city) & (df['year'] == year)]
    if len(row) > 0:
        for col in values:
            val = row[col].values[0]
            print(f"  {city} {year}年 {col} = {val}")

print(f"\n数据描述统计:")
print(df[['income', 'expend', 'gdp', 'gap', 'gap_to_gdp']].describe())

print("\n=== 数据补全完成 ===")
