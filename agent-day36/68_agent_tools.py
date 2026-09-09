import os
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

load_dotenv()

# ------------------------------------------------------------------
# 1. 定义自定义工具 (Tools)
# ------------------------------------------------------------------

@tool
def add_numbers(a: float, b: float) -> float:
    """计算两个数字的加法。对于精确的加法计算，必须调用此工具。"""
    return a + b

@tool
def multiply_numbers(a: float, b: float) -> float:
    """计算两个数字的乘法。对于精确的乘法计算，必须调用此工具。"""
    return a * b

@tool
def query_user_membership(user_id: str) -> str:
    """根据用户 ID 查询用户的会员等级与折扣。

    Args:
        user_id: 用户的唯一 ID，例如 'USR_101'
    """
    mock_users = {
        "USR_101": "用户：张三，等级：尊贵 VIP，享有 8 折优惠",
        "USR_102": "用户：李四，等级：普通会员，无折扣"
    }
    return mock_users.get(user_id, "未找到该用户 ID 的相关记录")

# 整理工具列表
tools = [add_numbers, multiply_numbers, query_user_membership]

# ------------------------------------------------------------------
# 2. 初始化 LLM 与 Prompt
# ------------------------------------------------------------------

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    temperature=0.0  # Agent 场景建议设为 0，保证调用的稳定性
)

# Tool-calling Agent 专用的 Prompt 结构
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个智能客服助手。对于数据计算和数据库查询，你必须严格使用提供的工具，严禁自主猜测。"),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"), # 用于存放 Agent 中间推理与工具调用的轨迹
])

# ------------------------------------------------------------------
# 3. 创建 Agent 与 AgentExecutor
# ------------------------------------------------------------------

# 创建基于原生 Tool Calling 能力的 Agent
agent = create_tool_calling_agent(llm, tools, prompt)

# 创建 Agent 执行器并设置安全边界
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,              # 打印 Agent 详细思考过程 (ReAct 轨迹)
    max_iterations=5,          # 最大迭代次数，防止无限循环
    handle_parsing_errors=True # 容错机制
)

# ------------------------------------------------------------------
# 4. 测试运行
# ------------------------------------------------------------------

if __name__ == "__main__":
    print("🤖 ===== 测试 1: 查询用户并结合计算 =====\n")
    query1 = "请查询用户 USR_101 的会员信息，如果他原价要买 250 元和 150 元的两件商品，打折前总价是多少？"
    response1 = agent_executor.invoke({"input": query1})
    print("\n最终回答:", response1["output"])

    print("\n" + "="*60 + "\n")

    print("🤖 ===== 测试 2: 触发精确乘法计算 =====\n")
    query2 = "计算 3.1415926 乘以 12.5 的精确结果是多少？"
    response2 = agent_executor.invoke({"input": query2})
    print("\n最终回答:", response2["output"])