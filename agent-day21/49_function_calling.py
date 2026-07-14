import os
import json
import sys
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=os.getenv("BASE_URL"))


# =====================================================================
# 🛠️ 1. 物理世界真实的本地函数实体 (Python Backend)
# =====================================================================
def get_current_weather(city: str) -> str:
    """真实的本地天气数据源"""
    city_clean = city.strip().lower()
    if "hangzhou" in city_clean:
        return json.dumps({"temp": 28.5, "unit": "celsius", "status": "Sunny"})
    elif "beijing" in city_clean:
        return json.dumps({"temp": 15.0, "unit": "celsius", "status": "Windy"})
    else:
        return json.dumps({"temp": 20.0, "unit": "celsius", "status": "Cloudy"})


def embedded_calculator(a: float, b: float, operator: str) -> str:
    """真实的本地计算器引擎"""
    if operator == "add":
        return str(a + b)
    elif operator == "subtract":
        return str(a - b)
    elif operator == "multiply":
        return str(a * b)
    elif operator == "divide":
        return str(a / b) if b != 0 else "Error: Division by zero"
    return "Error: Unknown operator"


# 建立工具字符串映射表，方便后续反射调用
TOOL_MAP = {
    "get_current_weather": get_current_weather,
    "embedded_calculator": embedded_calculator,
}

# =====================================================================
# 📋 2. 注入大模型的声明式 Schema 字典
# =====================================================================
# （见上方第二节定义的 TOOLS_SCHEMA，此处直接引入）
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "获取指定城市的实时天气温度信息。",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "城市名称，如 Hangzhou"}
                },
                "required": ["city"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "embedded_calculator",
            "description": "执行基础的数学四则运算。",
            "parameters": {
                "type": "object",
                "properties": {
                    "a": {"type": "number"},
                    "b": {"type": "number"},
                    "operator": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"],
                    },
                },
                "required": ["a", "b", "operator"],
            },
        },
    },
]


# =====================================================================
# 📡 3. 核心工具闭环有向图控制流
# =====================================================================
def run_agent_tool_loop(user_prompt: str):
    print(f"👤 [用户请求] ❯ {user_prompt}\n")

    # 构建初始消息体
    messages = [
        {
            "role": "system",
            "content": "你是一个高度自动化的全栈 Agent。善于利用工具解决问题，回答请简明扼要。",
        },
        {"role": "user", "content": user_prompt},
    ]

    # ========== 阶段 1: 将意图与工具池一同打向云端 ==========
    print("📡 [第一阶段] 正在向云端发射意图与 Tool Pool...")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=TOOLS_SCHEMA,  # 🌟 强行喂入本地工具规则
        tool_choice="auto",  # 让模型自主决定用不用、用哪个
        temperature=0.0,
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    # ========== 阶段 2: 拦截判定，是否有工具单下发 ==========
    if not tool_calls:
        print("🤖 [LLM 直出] 判定无需工具，直接返回内容：")
        print(response_message.content)
        return

    # 极其重要：如果大模型要求调用工具，必须把大模型含有 tool_calls 的“意图消息”追加进历史
    messages.append(response_message)

    # 处理并发或多重工具调用（大模型有时会一次下发多个工具单）
    for tool_call in tool_calls:
        function_name = tool_call.function.name
        # ⚠️ 翻车点拦截：arguments 是 JSON 字符串，必须解码！
        function_args = json.loads(tool_call.function.arguments)
        tool_id = tool_call.id

        print(f"🎯 [LLM 决策下发] ➡️ 匹配到工具: {function_name}")
        print(f"📦 [解构参数流]   ➡️ {function_args}")

        # 物理执行本地代码（反射执行）
        if function_name in TOOL_MAP:
            local_func = TOOL_MAP[function_name]
            # 运用 Python 逆向解构 **kwargs，完美对齐 JS 展开运算符 ...args
            actual_result = local_func(**function_args)

            print(f"⚙️ [本地物理执行] ➡️ 结果为: {actual_result}")

            # 🌟 极其重要：将工具回传报文追加进上下文，锁死 tool_id
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_id,
                    "name": function_name,
                    "content": actual_result,
                }
            )

    # ========== 阶段 3: 携带真实物理数据，二次绞杀大模型 ==========
    print("\n📡 [第三阶段] 携带物理世界回执，二次轰炸云端网关...")
    final_response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,  # 此时的 messages 包含了 user -> assistant(tool_calls) -> tool(results)
        temperature=0.0,
    )

    print("\n" + "=" * 50)
    print(f"🤖 [Agent 最终合流成果汇报] ❯")
    print(final_response.choices[0].message.content)
    print("=" * 50 + "\n")


if __name__ == "__main__":
    # 💥 测试用例：一个需要先跨越空间（天气查询）再进行数据加工（四则运算）的复合 Agent 请求
    complex_task = "帮我查一下杭州的天气，并帮我计算把这个温度乘以 3 之后是多少度？"
    run_agent_tool_loop(complex_task)
