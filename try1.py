from datetime import datetime

# 原始日期字符串
date_str = "2001-07-28"

# 将字符串转换为 datetime 对象
date_obj = datetime.strptime(date_str, "%Y-%m-%d")

# 格式化为所需的字符串格式，并手动去除月份和日期的前导零
formatted_date = f"{date_obj.year}年{date_obj.month}月{date_obj.day}日"

print(formatted_date)
