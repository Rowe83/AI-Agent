import os
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchResults
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain_core.tools import tool
from langchain_experimental.tools import PythonREPLTool

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

load_dotenv()

# =====================================================================
# 🛠️ 1. 实例化常用内置工具 (Built-in Tools)
# =====================================================================

# ① 内置工具 1：DuckDuckGo 实时网页搜索（网络不可达时返回错误信息，避免 Agent 崩溃）
_ddg = DuckDuckGoSearchResults()

@tool("duckduckgo_search")
def search_tool(query: str) -> str:
    """用于在互联网上搜索最新的新闻、实时事件或实时数据。"""
    try:
        return _ddg.run(query)
    except Exception as e:
        return (
            f"DuckDuckGo 搜索失败（网络不可达）: {type(e).__name__}: {e}。"
            "请改用其他可用工具，或基于已有知识作答并说明信息可能不是最新。"
        )

# ② 内置工具 2：Python REPL 执行器（用于精准数学计算、数据处理、逻辑验证）
python_repl_tool = PythonREPLTool(
    description="一个 Python 交互解释器。用于执行 Python 代码进行精准数学计算、逻辑推理或数据处理。"
)

# ③ 内置工具 3：Wikipedia 维基百科查询（国内网络常无法访问，捕获异常避免 Agent 中断）
_wiki_api = WikipediaAPIWrapper(top_k_results=1, doc_content_chars_max=1000)

@tool("wikipedia")
def wiki_tool(query: str) -> str:
    """用于查询维基百科中的概念、历史人物、科学定义等客观事实知识。"""
    try:
        return _wiki_api.run(query)
    except Exception as e:
        return (
            f"Wikipedia 查询失败（网络不可达）: {type(e).__name__}: {e}。"
            "请改用 duckduckgo_search，或基于已有知识简要回答。"
        )

# 汇总内置工具列表
tools = [search_tool, python_repl_tool, wiki_tool]

# =====================================================================
# 🤖 2. 初始化 LLM 与 Agent Prompt
# =====================================================================

llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    temperature=0.0  # Agent 工具调用场景建议设为 0
)

# 构建支持 Tool Calling 的标准 Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", (
        "你是一个全能的 AI 助手。"
        "对于实时新闻使用搜索工具，对于科学事实概念查询 Wikipedia，"
        "对于复杂计算、逻辑或数学问题，必须通过编写并运行 Python 代码解决。"
        "如果某个工具返回网络不可达或失败信息，请立刻改用其他工具或基于已有知识作答，不要反复调用同一失败工具。"
    )),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# =====================================================================
# 🚀 3. 构建 Agent 执行器
# =====================================================================

agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,              # 打印详细的思考轨迹 (Thought / Action / Observation)
    max_iterations=5,          # 安全保护：最大调用轮数
    handle_parsing_errors=True # 容错兜底
)

# =====================================================================
# 🧪 4. 测试不同场景下的内置工具自动调度
# =====================================================================

if __name__ == "__main__":
    print("="*60)
    print("测试 1：自动触发 Python REPL 进行复杂精细计算")
    print("="*60)
    # 大模型直接计算浮点数或斐波那契数列容易幻觉，Agent 会选择运行 Python 代码
    res1 = agent_executor.invoke({"input": "请帮我用代码计算第 30 个斐波那契数是多少？"})
    print("\n👉 最终回答:", res1["output"])

    print("\n" + "="*60)
    print("测试 2：自动触发 Wikipedia 检索知识概念")
    print("="*60)
    res2 = agent_executor.invoke({"input": "简要介绍一下概念 'Quantum entanglement' (量子纠缠) 是什么？"})
    print("\n👉 最终回答:", res2["output"])

    print("\n" + "="*60)
    print("测试 3：自动触发 DuckDuckGo 进行联网搜索")
    print("="*60)
    res3 = agent_executor.invoke({"input": "查询最近一次奥林匹克运动会（奥运会）是在哪里举办的？"})
    print("\n👉 最终回答:", res3["output"])