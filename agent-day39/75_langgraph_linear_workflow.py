from typing import TypedDict
from langgraph.graph import StateGraph, START, END

# 1. 定义全局 State 结构
class WorkflowState(TypedDict):
    input_text: str
    processed_text: str
    final_output: str

# 2. 定义节点函数（Node Functions）
def node_uppercase(state: WorkflowState) -> dict:
    print("--- 正在执行：转换为大写 ---")
    original = state["input_text"]
    # 返回对 State 的局部更新
    return {"processed_text": original.upper()}

def node_polish(state: WorkflowState) -> dict:
    print("--- 正在执行：结果润色 ---")
    processed = state["processed_text"]
    polished = f"✨ 格式化成功 -> {processed} (处理完毕)"
    return {"final_output": polished}

# 3. 初始化 StateGraph
workflow = StateGraph(WorkflowState)

# 4. 注册节点
workflow.add_node("uppercase_node", node_uppercase)
workflow.add_node("polish_node", node_polish)

# 5. 编排线性边（Linear Edges）：START -> uppercase_node -> polish_node -> END
workflow.add_edge(START, "uppercase_node")
workflow.add_edge("uppercase_node", "polish_node")
workflow.add_edge("polish_node", END)

# 6. 编译图（Compile the Graph）
app = workflow.compile()

# 7. 运行测试
if __name__ == "__main__":
    initial_state = {"input_text": "hello langgraph and ai world", "processed_text": "", "final_output": ""}

    print("🚀 开始运行线性工作流...\n")
    result = app.invoke(initial_state)

    print("\n" + "="*40)
    print("📌 最终输出结果:", result["final_output"])