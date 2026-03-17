# -*- coding: utf-8 -*-
"""从统计公报网站爬取昆明2009年缺失数据"""
import requests
import re
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 昆明2009年统计公报
url = "http://www.tjcn.org/tjgb/25yn/11727.html"
resp = requests.get(url, headers=headers, timeout=15)
resp.encoding = 'utf-8'
soup = BeautifulSoup(resp.text, 'html.parser')
text = soup.get_text()

# 搜索关键数据
print("=== 昆明2009年统计公报关键数据 ===")
# 查找预算收入
for line in text.split('\n'):
    line = line.strip()
    if any(kw in line for kw in ['预算收入', '预算支出', '储蓄存款', '居民存款']):
        if line:
            print(f"  {line[:200]}")
