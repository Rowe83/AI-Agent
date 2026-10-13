import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langgraph.checkpoint.memory import MemorySaver  # 👈 最新核心：短期状态快照器
from langgraph.prebuilt import create_react_agent

load_dotenv()

# 1. 定义工具
@tool
def get_user_balance(user_name: str) -> str:
    """查询指定用户的账户余额"""
    database = {"张三": "￥20,000.00", "李四": "￥150.00"}
    return database.get(user_name, "找不到该用户的记录")

tools = [get_user_balance]

# 2. 初始化大模型
model = ChatOpenAI(model="deepseek-v4-flash", temperature=0.0, api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=os.getenv("BASE_URL"))

# 3. 创建 Checkpointer (状态快照保存器)
checkpointer = MemorySaver()

# 4. 创建带 Checkpointer 的最新 ReAct Agent
agent = create_react_agent(
    model=model,
    tools=tools,
    checkpointer=checkpointer  # 👈 将记忆能力直接挂载到图图层
)

# 5. 执行多轮对话（必须提供 thread_id 来区分不同的用户/会话窗口）
config = {"configurable": {"thread_id": "session_user_888"}}

print("="*60)
print("💬 第 1 轮：告知 Agent 用户信息")
print("="*60)
response1 = agent.invoke(
    {"messages": [("user", "你好，我是张三，我是一名摄影师。")]},
    config=config
)
print("Agent:", response1["messages"][-1].content)

print("\n" + "="*60)
print("💬 第 2 轮：测试隐式记忆与工具调用 (未提到张三的名字)")
print("="*60)
# Agent 会自动回溯历史，得知“我”是张三，并调用工具查询张三的余额
response2 = agent.invoke(
    {"messages": [("user", "帮我查一下我的账户余额是多少？")]},
    config=config
)
print("Agent:", response2["messages"][-1].content)