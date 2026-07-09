# 1. 带有前后空格和换行符的用户昵称 (str)
raw_username = "   \n  Alex_Frontend_Lead   "

# 2. 从 API 拿到的原始工作年限字符串，结尾带了多余字符 (str)
raw_experience = "7years_experience"

# 3. 大模型当前计算出的系统延迟，包含高精度浮点数 (float)
raw_latency = 1.245893

# 4. 当前用户的账户会员状态（1 代表已激活，0 代表未激活）(int)
raw_is_vip = 1

# 5. 用户未配置自定义模型，系统返回的空值占位符 (NoneType)
raw_custom_model = None

print("=" * 40)
print("【AI 简历 SaaS 平台 - 运行日志】")
print("=" * 40)

username = raw_username.strip()  # 去除两端空格和换行
experience = int(raw_experience[:1])  # 取出年数并转换为整数

print(f"工程师姓名: {username.upper()} (已自动转大写)")
print(f"工作经验值: {experience} 年 (已成功转换为整数类型)")
print(f"Agent 延迟: {raw_latency:.2f} 秒 (要求：必须四舍五入保留两秒小数)")
print(f"VIP 会员 : {bool(raw_is_vip)} (要求：必须转换为真正的布尔类型)")
print(f"自定义模型: {raw_custom_model or '未配置'} (要求：若为 None，必须优雅显示为'未配置')")
print("-" * 40)
print(f"[DEBUG] {raw_latency=}, {raw_is_vip=}")
print("=" * 40)