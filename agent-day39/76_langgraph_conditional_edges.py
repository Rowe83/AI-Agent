from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# 1. 定义状态
class RouterState(TypedDict):
    user_query: str
    category: str
    response: str

# 2. 定义节点
def classifier_node(state: RouterState) -> dict:
    query = state["user_query"]
    print(f"🔍 [分类节点] 正在分析用户意图: {query}")
    
    # 简单的关键词判断逻辑（实际生产中可替换为 LLM 判断）
    if "代码" in query or "python" in query.lower():
        return {"category": "tech"}
    else:
        return {"category": "chat"}

def tech_support_node(state: RouterState) -> dict:
    print("⚙️ [技术支持节点] 正在生成技术解答...")
    return {"response": "这是一条针对程序员的技术支持回复：建议检查缩进和依赖包版本。"}

def general_chat_node(state: RouterState) -> dict:
    print("💬 [闲聊节点] 正在生成日常对话回复...")
    return {"response": "你好呀！很高兴和你聊天，今天有什么我可以帮你的吗？"}

# 3. 定义路由分发函数 (Routing Function)
def route_decision(state: RouterState) -> str:
    """根据 category 状态返回下一个要执行的节点名称"""
    cat = state["category"]
    if cat == "tech":
        return "tech_node"
    else:
        return "general_node"

# 4. 构建图
router_workflow = StateGraph(RouterState)

router_workflow.add_node("classifier", classifier_node)
router_workflow.add_node("tech_node", tech_support_node)
router_workflow.add_node("general_node", general_chat_node)

# 5. 设置边与条件边
router_workflow.add_edge(START, "classifier")

# 核心：添加条件边 (Conditional Edge)
# 参数 1: 起始节点
# 参数 2: 路由判断函数 (返回字符串，对应后面的映射 key)
# 参数 3: 映射字典 (Key -> 节点名称)
router_workflow.add_conditional_edges(
    "classifier",
    route_decision,
    {
        "tech_node": "tech_node",
        "general_node": "general_node"
    }
)

router_workflow.add_edge("tech_node", END)
router_workflow.add_edge("general_node", END)

# 编译
router_app = router_workflow.compile()

# 6. 测试运行
if __name__ == "__main__":
    print("="*60)
    print("测试分支 1：触发技术支持分支")
    print("="*60)
    res1 = router_app.invoke({"user_query": "我的 Python 代码报错了怎么解决？", "category": "", "response": ""})
    print("👉 回复:", res1["response"])

    print("\n" + "="*60)
    print("测试分支 2：触发闲聊分支")
    print("="*60)
    res2 = router_app.invoke({"user_query": "今天天气真不错，你吃了没？", "category": "", "response": ""})
    print("👉 回复:", res2["response"])