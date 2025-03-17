import requests
from bs4 import BeautifulSoup
import re
import time
import random
import pandas as pd
from datetime import datetime
import os

# 请求头，模拟浏览器访问
headers = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                   'AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/90.0.4430.93 Safari/537.36')
}

# 分页设置：设定要爬取的页数
num_pages = 1  # 可根据需要调整页数

# 用于存储所有详情页链接，保持顺序
all_subject_urls = []

for page in range(1, num_pages + 1):
    # 构造分页URL
    if page == 1:
        page_url = "https://bangumi.tv/anime/browser/?sort=rank"
    else:
        page_url = f"https://bangumi.tv/anime/browser/?sort=rank&page={page}"

    print(f"正在爬取第 {page} 页：{page_url}")
    response = requests.get(page_url, headers=headers)

    if response.status_code != 200:
        print(f"无法请求第 {page} 页，跳过")
        continue

    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    # 提取所有详情页链接（按出现顺序），避免重复
    for a in soup.find_all('a', href=re.compile(r'^/subject/\d+')):
        link = a['href']
        if link not in all_subject_urls:
            all_subject_urls.append(link)

# 将相对链接转换为完整链接
subject_urls = ["https://bangumi.tv" + link for link in all_subject_urls]
print(f"共找到 {len(subject_urls)} 个详情页链接")

results = []
# 使用 enumerate 保证排名顺序（从1开始）
for ranking, url in enumerate(subject_urls, start=1):
    print(f"处理排名 {ranking} 的动画：{url}")
    try:
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print(f"请求失败: {url}")
            continue

        r.encoding = 'utf-8'
        subject_soup = BeautifulSoup(r.text, 'html.parser')
        air_date = None

        # 方法1：查找包含关键词的 <li> 标签
        li_tag = subject_soup.find(lambda tag: tag.name == "li" and any(
            keyword in tag.get_text() for keyword in ["放送开始", "上映年度", "开始", "首播"]
        ))
        if li_tag:
            match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日)|(\d{4}年)', li_tag.get_text())
            if match:
                air_date = match.group(0)

        # 方法2：查找 <span> 标签，尝试匹配“首播:YYYY-MM-DD”格式
        if not air_date:
            span_tag = subject_soup.find('span', class_='tip')
            if span_tag:
                match = re.search(r'首播:(\d{4}-\d{2}-\d{2})', span_tag.get_text())
                if match:
                    air_date = match.group(1)

        # 方法3：查找 <div> 标签，尝试匹配“首播:YYYY-MM-DD”格式
        if not air_date:
            div_tag = subject_soup.find('div', id=re.compile(r'prginfo_\d+'))
            if div_tag:
                match = re.search(r'首播:(\d{4}-\d{2}-\d{2})', div_tag.get_text())
                if match:
                    air_date = match.group(1)

        # 将日期格式统一为“YYYY年M月D日”
        formatted_date = None
        if air_date:
            try:
                if '年' in air_date:
                    # 已经是“YYYY年M月D日”格式
                    formatted_date = air_date
                else:
                    # 将“YYYY-MM-DD”格式转换为“YYYY年M月D日”
                    date_obj = datetime.strptime(air_date, "%Y-%m-%d")
                    formatted_date = f"{date_obj.year}年{date_obj.month}月{date_obj.day}日"
            except ValueError as ve:
                print(f"日期格式错误: {ve}")
                formatted_date = air_date
        else:
            print("未找到相关的日期信息")

        results.append({
            'rank': ranking,
            'url': url,
            'air_date': formatted_date
        })
    except Exception as e:
        print(f"处理时发生错误: {e}")

    # 延时 1 秒加上 0~1 秒之间的随机数，防止请求过快
    time.sleep(1 + random.random())

# 将结果转换为 DataFrame 并输出
df = pd.DataFrame(results)
print(df)

# 保存结果到 CSV 文件（如果存在则覆盖，可根据需要改为追加模式）
output_file = "bangumi_ranking.csv"
df.to_csv(output_file, index=False, encoding="utf-8-sig")
print(f"数据已保存到 {output_file}")
