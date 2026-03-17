# -*- coding: utf-8 -*-
"""从统计公报网站爬取缺失数据"""
import requests
import re
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

def fetch_page(url):
    resp = requests.get(url, headers=headers, timeout=15)
    # 尝试多种编码
    for enc in ['utf-8', 'gbk', 'gb2312', 'gb18030']:
        try:
            resp.encoding = enc
            text = resp.text
            if '统计' in text or '公报' in text:
                return text
        except:
            pass
    resp.encoding = resp.apparent_encoding
    return resp.text

# 昆明2009年统计公报
print("=== 昆明2009年 ===")
url = "http://www.tjcn.org/tjgb/25yn/11727.html"
html = fetch_page(url)
soup = BeautifulSoup(html, 'html.parser')
text = soup.get_text()

# 打印所有包含关键词的行
for line in text.split('\n'):
    line = line.strip()
    if len(line) > 5 and any(kw in line for kw in ['预算收入', '预算支出', '储蓄', '居民存款', '生产总值']):
        print(f"  {line[:300]}")

# 也直接搜索数字模式
matches = re.findall(r'一般预算收入[^。]*?[\d,.]+[^。]*?[万亿]元', text)
print(f"\n预算收入匹配: {matches}")
matches2 = re.findall(r'一般预算支出[^。]*?[\d,.]+[^。]*?[万亿]元', text)
print(f"预算支出匹配: {matches2}")
matches3 = re.findall(r'储蓄存款[^。]*?[\d,.]+[^。]*?[万亿]元', text)
print(f"储蓄存款匹配: {matches3}")

# 打印前3000字符看看
print(f"\n--- 页面前3000字 ---")
print(text[:3000])
