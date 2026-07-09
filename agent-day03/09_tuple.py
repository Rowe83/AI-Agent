# 1. 语义上的“只读安全”（防篡改配置）
# 核心配置文件，防止在复杂的 Agent 异步长链路中被其他模块意外修改
LLM_GATEWAY_CONFIG = ("https://api.openai.com/v1", 30, "gpt-4o")

# 2. 函数多返回值（解构赋值的天然载体）
def parse_limit_usage():
    num1 = 100
    num2 = 200
    return num1, num2

num1, num2 = parse_limit_usage()
print(f"解构赋值： {num1}, {num2}")  # 输出: 100 200

# 3. 可以作为字典（Dict）的 Key（列表绝对不行）
# 用（当前智能体，当前状态）组成的元组，来作为映射字典的 Key
agent_routes = {
    ("RouterAgent", "success"): "ExecutorAgent",
    ("RouterAgent", "failed"): "HumanReviewNode",
}

next_node = agent_routes.get(("RouterAgent", "success"))
print(f"下一步流转至: {next_node}")  # 输出: ExecutorAgent

# 4. 极致的性能优化（高并发吞吐）
# 内存占用小： 元组因为大小固定，在 Python 内存中是线性连续紧凑分配的；而列表为了支持 append，底层预留了超额的内存空间（Over-allocation）。
# 创建速度快： 在高并发、百万级大模型 Token 流处理的场景下，创建元组的速度显著快于列表。