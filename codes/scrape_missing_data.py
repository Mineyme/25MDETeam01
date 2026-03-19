# -*- coding: utf-8 -*-
"""
数据补全爬虫脚本
从统计公报网站(http://www.tjcn.org/tjgb/)爬取国家统计局缺失的城市数据

缺失数据清单:
- 哈尔滨 2022: income, expend
- 昆明 2009: income, expend, deposit
- 拉萨 2006: gdp, deposit
- 拉萨 2010: gdp, deposit
- 拉萨 2012: deposit
- 拉萨 2013: deposit
"""
import requests
import re
from bs4 import BeautifulSoup
import json
import os

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def fetch_page(url):
    """获取网页内容，自动处理编码"""
    resp = requests.get(url, headers=headers, timeout=15)
    for enc in ['utf-8', 'gbk', 'gb2312', 'gb18030']:
        try:
            resp.encoding = enc
            text = resp.text
            if '统计' in text or '公报' in text or '经济' in text:
                return text
        except:
            pass
    resp.encoding = resp.apparent_encoding
    return resp.text

def extract_text(html):
    """从HTML提取纯文本"""
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()

def search_number(text, keyword, unit='亿元'):
    """从文本中搜索关键词后面的数字"""
    # 模式: 关键词...数字...单位
    pattern = rf'{keyword}[^。]*?([\d,]+\.?\d*)\s*{unit}'
    matches = re.findall(pattern, text)
    if matches:
        return float(matches[0].replace(',', ''))
    return None

# ============================================================
# 爬取各城市统计公报
# ============================================================

results = {}

# --- 1. 哈尔滨 2022年 ---
print("=" * 60)
print("1. 爬取哈尔滨2022年统计公报")
print("=" * 60)

# 哈尔滨2022年统计公报
urls_harbin = [
    "http://www.tjcn.org/tjgb/07hlj/40339.html",
    "http://www.tjcn.org/tjgb/07hlj/40339_2.html",
]

harbin_text = ""
for url in urls_harbin:
    try:
        html = fetch_page(url)
        harbin_text += extract_text(html)
    except Exception as e:
        print(f"  Failed: {url} - {e}")

if harbin_text:
    income = search_number(harbin_text, '一般公共预算收入')
    expend = search_number(harbin_text, '一般公共预算支出')
    print(f"  一般公共预算收入: {income} 亿元")
    print(f"  一般公共预算支出: {expend} 亿元")
    # 用户提供的数据: 收入262.2亿元, 支出1065.5亿元
    if income is None:
        income = 262.2
        print(f"  [使用用户提供数据] 一般公共预算收入: {income} 亿元")
    if expend is None:
        expend = 1065.5
        print(f"  [使用用户提供数据] 一般公共预算支出: {expend} 亿元")
    results['哈尔滨_2022'] = {'income': income, 'expend': expend}
else:
    # 使用用户提供的数据
    results['哈尔滨_2022'] = {'income': 262.2, 'expend': 1065.5}
    print("  [使用用户提供数据] income=262.2, expend=1065.5")

# --- 2. 昆明 2009年 ---
print("\n" + "=" * 60)
print("2. 爬取昆明2009年统计公报")
print("=" * 60)

url_km = "http://www.tjcn.org/tjgb/25yn/11727.html"
try:
    html = fetch_page(url_km)
    km_text = extract_text(html)
    
    income = search_number(km_text, '一般预算收入')
    expend = search_number(km_text, '一般预算支出')
    deposit = search_number(km_text, '储蓄存款余额')
    
    print(f"  一般预算收入: {income} 亿元")
    print(f"  一般预算支出: {expend} 亿元")
    print(f"  储蓄存款余额: {deposit} 亿元")
    
    # 用户提供: 收入2,016,125万元=201.6125亿元, 支出2,704,495万元=270.4495亿元, 储蓄1922.92亿元
    if income is None:
        income = 201.6125
    if expend is None:
        expend = 270.4495
    if deposit is None:
        deposit = 1922.92
    
    results['昆明_2009'] = {'income': income, 'expend': expend, 'deposit': deposit}
except Exception as e:
    print(f"  Failed: {e}")
    results['昆明_2009'] = {'income': 201.6125, 'expend': 270.4495, 'deposit': 1922.92}

# --- 3. 拉萨 2006年 ---
print("\n" + "=" * 60)
print("3. 爬取拉萨2006年统计公报")
print("=" * 60)

url_ls_2006 = "https://web.xiaze.org/tjgb/201009/30764.html"
try:
    html = fetch_page(url_ls_2006)
    ls_text = extract_text(html)
    
    gdp = search_number(ls_text, '生产总值.*?GDP.*?')
    if gdp is None:
        gdp = search_number(ls_text, '生产总值')
    deposit = search_number(ls_text, '储蓄存款')
    
    print(f"  GDP: {gdp} 亿元")
    print(f"  储蓄存款余额: {deposit} 亿元")
    
    # 用户提供: GDP=102.39亿元, 储蓄存款=78.99亿元
    if gdp is None:
        gdp = 102.39
    if deposit is None:
        deposit = 78.99
    
    results['拉萨_2006'] = {'gdp': gdp, 'deposit': deposit}
except Exception as e:
    print(f"  Failed: {e}")
    results['拉萨_2006'] = {'gdp': 102.39, 'deposit': 78.99}

# --- 4. 拉萨 2010年 ---
print("\n" + "=" * 60)
print("4. 爬取拉萨2010年统计公报")
print("=" * 60)

url_ls_2010 = "http://www.tjcn.org/tjgb/26xz/20306.html"
try:
    html = fetch_page(url_ls_2010)
    ls_text = extract_text(html)
    
    gdp = search_number(ls_text, '生产总值')
    deposit = search_number(ls_text, '储蓄存款余额')
    if deposit is None:
        deposit = search_number(ls_text, '储蓄存款')
    
    print(f"  GDP: {gdp} 亿元")
    print(f"  储蓄存款余额: {deposit} 亿元")
    
    # 用户提供: GDP=178.91亿元, 储蓄存款=151.03亿元
    if gdp is None:
        gdp = 178.91
    if deposit is None:
        deposit = 151.03
    
    results['拉萨_2010'] = {'gdp': gdp, 'deposit': deposit}
except Exception as e:
    print(f"  Failed: {e}")
    results['拉萨_2010'] = {'gdp': 178.91, 'deposit': 151.03}

# --- 5. 拉萨 2012年 ---
print("\n" + "=" * 60)
print("5. 拉萨2012年 (用户提供数据)")
print("=" * 60)
# 用户提供: 人民币个人储蓄存款余额223.83亿元
results['拉萨_2012'] = {'deposit': 223.83}
print(f"  储蓄存款余额: 223.83 亿元 (用户提供)")

# --- 6. 拉萨 2013年 ---
print("\n" + "=" * 60)
print("6. 拉萨2013年 (用户提供数据)")
print("=" * 60)
# 用户提供: 人民币个人储蓄存款余额272.12亿元
results['拉萨_2013'] = {'deposit': 272.12}
print(f"  储蓄存款余额: 272.12 亿元 (用户提供)")

# ============================================================
# 保存爬取结果
# ============================================================
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
output_path = os.path.join(project_root,"data_raw", "missing_data_scraped.json")
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n{'='*60}")
print(f"爬取结果已保存: {output_path}")
print(f"{'='*60}")
print(json.dumps(results, ensure_ascii=False, indent=2))
