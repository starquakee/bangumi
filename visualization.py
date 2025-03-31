import matplotlib.pyplot as plt
import pandas as pd
import re
import seaborn as sns

# ---------------------- 设置全局风格 ----------------------
sns.set_theme(context="notebook", style="whitegrid", font="Microsoft YaHei", font_scale=1.2)
plt.rcParams['axes.unicode_minus'] = False

# ---------------------- 读取数据并提取年份 ----------------------
df = pd.read_csv('data/bangumi_ranking.csv')

def extract_year(date_str):
    """从 air_date 中提取4位年份"""
    match = re.search(r'(\d{4})', str(date_str))
    return int(match.group(1)) if match else None

df['year'] = df['air_date'].apply(extract_year)
df_valid = df.dropna(subset=['year'])
df_valid = df_valid[df_valid['year'] >= 1990]

# ---------------------- 提取月份和计算季度 ----------------------
def extract_month(date_str):
    """从日期字符串中提取月份（支持中文日期和'-MM-'形式）"""
    match = re.search(r'(\d{1,2})月', str(date_str))
    if match:
        return int(match.group(1))
    match = re.search(r'\d{4}-(\d{2})-\d{2}', str(date_str))
    return int(match.group(1)) if match else None

df_valid['month'] = df_valid['air_date'].apply(extract_month)

def get_quarter(month):
    """根据月份返回季度标识：1-3月为"1月"，4-6月为"4月"，7-9月为"7月"，10-12月为"10月" """
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

df_valid['quarter'] = df_valid['month'].apply(get_quarter)

# ---------------------- 图1：散点图，展示年份与作品排名 ----------------------
plt.figure(figsize=(8, 6))
plt.scatter(df_valid['year'], df_valid['rank'], alpha=0.4, edgecolor='w', s=60)
plt.xlabel('上映年份')
plt.ylabel('作品排名')
plt.title('年份与作品排名之间的关系')
plt.gca().invert_yaxis()  # 使排名1在图表上方
plt.tight_layout()
plt.show()

# ---------------------- 图2：箱线图，展示不同年份作品排名分布 ----------------------
plt.figure(figsize=(10, 6))
sns.boxplot(x='year', y='rank', data=df_valid, palette="Set3")
plt.gca().invert_yaxis()
plt.xticks(rotation=45)
plt.title('不同年份作品排名分布')
plt.tight_layout()
plt.show()

# ---------------------- 图3：柱状图，展示每年作品的平均排名 ----------------------
yearly_mean_rank = df_valid.groupby('year')['rank'].mean().reset_index()
plt.figure(figsize=(10, 6))
plt.bar(yearly_mean_rank['year'], yearly_mean_rank['rank'], color=sns.color_palette("viridis", len(yearly_mean_rank)))
plt.xlabel('上映年份')
plt.ylabel('平均排名')
plt.title('不同年份作品平均排名')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()

# ---------------------- 图4：柱状图，展示每年的作品数量 ----------------------
yearly_count = df_valid.groupby('year').size().reset_index(name='count')
plt.figure(figsize=(10, 6))
plt.bar(yearly_count['year'], yearly_count['count'], color=sns.color_palette("magma", len(yearly_count)))
plt.xlabel('上映年份')
plt.ylabel('作品数量')
plt.title('不同年份作品数量')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# ---------------------- 图5：热力图，展示每年各季度动画的中位数排名 ----------------------
df_quarter = df_valid.dropna(subset=['quarter'])
quarter_median = df_quarter.groupby(['year', 'quarter'])['rank'].median().reset_index()
quarter_order = ["1月", "4月", "7月", "10月"]
pivot_table = quarter_median.pivot(index='year', columns='quarter', values='rank')[quarter_order]

plt.figure(figsize=(12, 8))
ax = sns.heatmap(pivot_table, annot=True, fmt=".1f", cmap="YlGnBu", cbar_kws={'label': '中位数排名'}, linewidths=.5)
plt.xlabel('季度')
plt.ylabel('上映年份')
plt.title('每年各季度动画中位数排名')
plt.tight_layout()
plt.show()

# ---------------------- 图6：柱状图，展示1990年来每年前1000名的动画数量 ----------------------
df_top1000 = df_valid[df_valid['rank'] <= 1000]
yearly_top_count = df_top1000.groupby('year').size().reset_index(name='count')

plt.figure(figsize=(10, 6))
plt.bar(yearly_top_count['year'], yearly_top_count['count'], color=sns.color_palette("coolwarm", len(yearly_top_count)))
plt.xlabel('上映年份')
plt.ylabel('前1000名动画数量')
plt.title('1990年来每年前1000名动画数量')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
