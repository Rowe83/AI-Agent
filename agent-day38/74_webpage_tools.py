import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
import requests
from bs4 import BeautifulSoup
from langchain.agents import create_agent
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# 1. 准备工具集
_ddg = DuckDuckGoSearchRun()

@tool("duckduckgo_search")
def search_tool(query: str) -> str:
    """用于在互联网上搜索相关文章、资讯或网站链接。"""
    try:
        return _ddg.run(query)
    except Exception as e:
        return f"搜索失败（网络不可达）: {type(e).__name__}: {e}"

@tool
def fetch_webpage_content(url: str) -> str:
    """抓取指定 URL 网页的正文纯文本内容。当需要深入阅读某个链接的具体内容时调用此工具。
    
    Args:
        url: 目标网页的完整链接
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        response = requests.get(url, headers=headers, timeout=8)
        soup = BeautifulSoup(response.text, "html.parser")
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
        text = soup.get_text()
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)[:5000] # 限制返回内容长度
    except Exception as e:
        return f"获取网页内容失败: {e}"

tools = [search_tool, fetch_webpage_content]

# 2. 初始化大模型
model = ChatOpenAI(
    model="deepseek-v4-flash",
    temperature=0.0,
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL")
)

# 3. 创建带有短期记忆的 Agent（LangChain 1.x：create_agent + checkpointer）
agent = create_agent(
    model=model,
    tools=tools,
    checkpointer=MemorySaver(),
    system_prompt="你是一个全能的信息搜集研究员。当用户让你了解某个事件或文章时，请先使用搜索工具找到链接，然后使用网页抓取工具深入阅读并总结。"
)

# 4. 执行测试
if __name__ == "__main__":
    config = {"configurable": {"thread_id": "research_session_001"}}

    query = "请帮我搜索了解一下 2026 年人工智能领域最新的技术突破，并找一篇相关的报道总结核心要点。"
    print(f"🤖 用户指令: {query}\n" + "-"*50)

    # 运行 Agent 闭环
    for step in agent.stream({"messages": [("user", query)]}, config=config, stream_mode="values"):
        latest_msg = step["messages"][-1]
        latest_msg.pretty_print()
