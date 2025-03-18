import matplotlib
import pandas as pd
import re
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------- 读取数据并提取年份 ----------------------
# 读取 CSV 文件（默认逗号分隔，如果是 TSV 则需要指定 sep='\t'）
df = pd.read_csv('bangumi_ranking.csv')

# 定义函数：从 air_date 中提取 4 位年份
def extract_year(date_str):
    match = re.search(r'(\d{4})', str(date_str))
    if match:
        return int(match.group(1))
    return None

# 新增年份列
df['year'] = df['air_date'].apply(extract_year)

# 筛选上映年份 >= 1990 的数据
df_valid = df.dropna(subset=['year'])
df_valid = df_valid[df_valid['year'] >= 1990]

# ---------------------- 提取月份和计算季度 ----------------------
def extract_month(date_str):
    """
    尝试从日期字符串中提取月份（例如“2003年6月11日”或“2003-06-11”）
    """
    # 优先匹配包含中文“月”的情况
    match = re.search(r'(\d{1,2})月', str(date_str))
    if match:
        return int(match.group(1))
    # 否则匹配"-MM-"形式
    match = re.search(r'\d{4}-(\d{2})-\d{2}', str(date_str))
    if match:
        return int(match.group(1))
    return None

# 新增月份列
df_valid['month'] = df_valid['air_date'].apply(extract_month)

def get_quarter(month):
    """
    根据月份返回季度标识：1-3月为"1月"，4-6月为"4月"，7-9月为"7月"，10-12月为"10月"
    """
    if month is None:
        return None
    if 1 <= month <= 3:
        return "1月"
    elif 4 <= month <= 6:
        return "4月"
    elif 7 <= month <= 9:
        return "7月"
    elif 10 <= month <= 12:
        return "10月"
    return None

# 计算季度，只有存在月份信息的行有效
df_valid['quarter'] = df_valid['month'].apply(get_quarter)

# ---------------------- 配置 matplotlib 字体 ----------------------
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 使用微软雅黑显示中文
plt.rcParams['axes.unicode_minus'] = False
# matplotlib.use('TkAgg')  # 若在 PyCharm 中使用 SciView，建议注释此行

# ---------------------- 图1：散点图，展示年份与作品排名 ----------------------
plt.figure(figsize=(8, 6))
plt.scatter(df_valid['year'], df_valid['rank'], alpha=0.2)
plt.xlabel('上映年份')
plt.ylabel('作品排名')
plt.title('年份与作品排名之间的关系')
plt.gca().invert_yaxis()  # 使排名1在图表上方
plt.show()

# ---------------------- 图2：箱线图，展示不同年份作品排名分布 ----------------------
plt.figure(figsize=(10, 6))
sns.boxplot(x='year', y='rank', data=df_valid)
plt.gca().invert_yaxis()
plt.xticks(rotation=45)
plt.title('不同年份作品排名分布')
plt.show()

# ---------------------- 图3：柱状图，展示每年作品的平均排名 ----------------------
yearly_mean_rank = df_valid.groupby('year')['rank'].mean().reset_index()
plt.figure(figsize=(10, 6))
plt.bar(yearly_mean_rank['year'], yearly_mean_rank['rank'])
plt.xlabel('上映年份')
plt.ylabel('平均排名')
plt.title('不同年份作品平均排名')
plt.gca().invert_yaxis()
plt.show()

# ---------------------- 图4：柱状图，展示每年的作品数量 ----------------------
yearly_count = df_valid.groupby('year').size().reset_index(name='count')
plt.figure(figsize=(10, 6))
plt.bar(yearly_count['year'], yearly_count['count'])
plt.xlabel('上映年份')
plt.ylabel('作品数量')
plt.title('不同年份作品数量')
plt.xticks(rotation=45)
plt.show()

# ---------------------- 图5：热力图，展示每年各季度动画的中位数排名 ----------------------
# 过滤掉没有季度信息的记录
df_quarter = df_valid.dropna(subset=['quarter'])

# 按年份和季度计算中位数排名
quarter_median = df_quarter.groupby(['year', 'quarter'])['rank'].median().reset_index()

# 将数据透视成矩阵形式，行：年份，列：季度
# 为保证季度顺序，设置列顺序
quarter_order = ["1月", "4月", "7月", "10月"]
pivot_table = quarter_median.pivot(index='year', columns='quarter', values='rank')[quarter_order]

plt.figure(figsize=(12, 8))
sns.heatmap(pivot_table, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={'label': '中位数排名'})
plt.xlabel('季度')
plt.ylabel('上映年份')
plt.title('每年各季度动画中位数排名')
plt.show()
