import os
import sqlite3
from dotenv import load_dotenv
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool

load_dotenv()

@tool
def get_user_balance(user_name: str) -> str:
    """查询指定用户的账户余额"""
    database = {"张三": "￥20,000.00", "李四": "￥150.00"}
    return database.get(user_name, "找不到该用户的记录")

tools = [get_user_balance]

# 1. 连接/创建本地 SQLite 数据库文件
conn = sqlite3.connect("agent_memory.db", check_same_thread=False)

# 2. 使用 SqliteSaver 替代 MemorySaver
with SqliteSaver(conn) as sqlite_checkpointer:
    
    agent = create_react_agent(
        model=ChatOpenAI(model="deepseek-v4-flash", temperature=0.0, api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=os.getenv("BASE_URL")),
        tools=tools,
        checkpointer=sqlite_checkpointer # 👈 切换为 SQLite 存储
    )

    # 3. 指定特定的会话 ID
    config = {"configurable": {"thread_id": "vip_customer_001"}}

    # 执行对话...即便重启 Python 代码，只要数据库文件在，历史依然完整读取！
    res = agent.invoke({"messages": [("user", "我上次让你帮我记的事你还记得吗？")]}, config=config)
    print(res["messages"][-1].content)