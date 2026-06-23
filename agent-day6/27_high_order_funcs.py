# 1. 模拟上游拉取到的三路异步数据流水
modules = ["Next.js SSR", "Database Query", "DeepSeek API", "Tailwind Compile"]
latencies = [0.12, 0.45, 2.85, 0.08]  # 单位: 秒
statuses = ["SUCCESS", "SUCCESS", "SUCCESS", "FAILED"]

print("1. 🔗 正在启动 zip() 跨队列拉链咬合...")
print(list(zip(modules, latencies, statuses)))
# 将三路数据无缝并排绑定，通过列表推导式直接组装成结构化字典列表
pipeline_data = [
    {"module": mod, "time": t, "status": s} 
    for mod, t, s in zip(modules, latencies, statuses)
]

# 2. 打印看一下拼装结果
for item in pipeline_data:
    print(f"   已归档: {item}")
print("-" * 50)

print("2. 🧼 正在使用 filter() 与 lambda 筛选出耗时严重（>0.4秒）或失败的阻塞节点：")
# 筛选条件：时间 > 0.4 秒 或者 状态不是 SUCCESS
is_blocked = lambda x: x["time"] > 0.4 or x["status"] != "SUCCESS"

blocked_nodes = list(filter(is_blocked, pipeline_data))

# 3. 完美输出审计结果
for node in blocked_nodes:
    print(f"   🛑 [阻塞告警] 模块: {node['module']} | 耗时: {node['time']}s | 状态: {node['status']}")