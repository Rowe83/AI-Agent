user_role = "VIP"
current_concurrency = 15

print("开始执行安全路由控制逻辑...\n" + "="*50)

if user_role == "ADMIN":
    print("放行：管理员用户，无并发限制")
elif user_role == "VIP" and current_concurrency <= 20:
    print("放行：VIP 用户，并发量在安全范围内")
elif user_role == "FREE" and current_concurrency <= 5:
    print("放行：免费用户，并发量在安全范围内")
else:
    print("拒绝访问：并发量过高或用户权限不足")

http_status = 200 if current_concurrency <= 20 else 429

print(f"HTTP 响应状态码: {http_status}")