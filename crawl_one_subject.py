import re
from datetime import datetime

import requests
import chardet
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36'
}
url = 'https://bangumi.tv/subject/209063'
r = requests.get(url, headers=headers)
r.encoding = 'utf-8'
subject_soup = BeautifulSoup(r.text, 'html.parser')
air_date = None
print(r.text)
# 方法1：查找包含关键词的 <li> 标签
li_tag = subject_soup.find(lambda tag: tag.name == "li" and any(
    keyword in tag.get_text() for keyword in ["放送开始", "上映年度", "开始", "首播", "发售日"]
))
if li_tag:
    match = re.search(r'(\d{4}-\d{2}-\d{2})|(\d{4}年\d{1,2}月\d{1,2}日)|(\d{4}年)|(\d{4})(?![-年])', li_tag.get_text())
    if match:
        air_date = match.group(0)
        print(1)

# 方法2：查找 <span> 标签，尝试匹配“首播:YYYY-MM-DD”格式
if not air_date:
    span_tag = subject_soup.find('span', class_='tip')
    if span_tag:
        match = re.search(r'首播:(\d{4}-\d{2}-\d{2})', span_tag.get_text())
        if match:
            air_date = match.group(1)
            print(2)

# 方法3：查找 <div> 标签，尝试匹配“首播:YYYY-MM-DD”格式
if not air_date:
    div_tag = subject_soup.find('div', id=re.compile(r'prginfo_\d+'))
    if div_tag:
        match = re.search(r'首播:(\d{4}-\d{2}-\d{2})', div_tag.get_text())
        if match:
            air_date = match.group(1)
            print(3)

print(air_date)
if air_date:
    try:
        if '-' in air_date:
            # 如果格式是“YYYY-MM-DD”，转换为“YYYY年M月D日”
            date_obj = datetime.strptime(air_date, "%Y-%m-%d")
            formatted_date = f"{date_obj.year}年{date_obj.month}月{date_obj.day}日"
        elif len(air_date) == 4 and air_date.isdigit():
            # 如果只是4位数字（纯年份）
            formatted_date = f"{air_date}年"
        else:
            formatted_date = air_date
    except ValueError as ve:
        print(f"日期格式错误: {ve}")
        formatted_date = air_date
else:
    print("未找到相关的日期信息")
print(formatted_date)
