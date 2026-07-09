# 1. 先定义两个真实的确定性本地工具函数
def get_weather(city: str) -> str:
    return f"🌤️ {city} 当前天气：晴，25°C"

def generate_image(prompt: str) -> str:
    return f"🎨 已根据提示词 [{prompt}] 渲染出 A4 规格高清图片"

# 2. 核心：建立工具路由表（将字符串映射为真实的函数对象）
# 💡 前端心智：这完美对齐了 JS 中将函数作为一等公民（First-Class Functions）存入 Object 的操作
tool_marketplace = {
    "weather_tool": get_weather,
    "image_tool": generate_image
}

# 3. 模拟大模型理解意图后，吐出来的结构化 JSON 数据
llm_response = {
    "called_tool": "weather_tool",
    "arguments": {"city": "杭州"}
}

# 4. 安全路由控制流
tool_name = llm_response.get("called_tool")
args = llm_response.get("arguments", {})

# 从字典中抓取真正的函数指针
chosen_tool = tool_marketplace.get(tool_name)

print("🤖 Agent 工具路由激活...")
if chosen_tool:
    # 动态执行函数，并将字典作为关键字参数解构传进去（**args 相当于 JS 的 ...args）
    result = chosen_tool(**args)
    print(f"🎯 工具执行结果: {result}")
else:
    print("❌ 错误：大模型乱编了一个不存在的工具名称！")