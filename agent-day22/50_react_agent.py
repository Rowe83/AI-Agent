import os
import re
import sys
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=os.getenv("BASE_URL"))


# =====================================================================
# 🛠️ 1. 物理世界真实工具箱
# =====================================================================
def mock_wiki_search(query: str) -> str:
    """模拟维基百科高价值事实搜索"""
    q_clean = query.strip().lower()
    if "apple" in q_clean or "苹果" in q_clean:
        return "苹果公司（Apple）当前市值为 3.5 万亿美元。"
    elif "google" in q_clean or "谷歌" in q_clean:
        return "谷歌公司（Google/Alphabet）当前市值为 2.0 万亿美元。"
    return "未找到相关实体的事实数据。"


def embedded_calculator(expression: str) -> str:
    """安全的本地物理计算器"""
    # 过滤掉非法字符，只允许基础数学运算
    clean_expr = re.sub(r"[^0-9\+\-\*\/\(\)\. ]", "", expression)
    try:
        # eval 虽好，生产环境建议使用 ast.literal_eval 或专门的计算库
        return str(eval(clean_expr))
    except Exception as e:
        return f"Error: 无法计算表达式 '{expression}', 详情: {e}"


# 物理工具映射表
TOOL_BOX = {"search": mock_wiki_search, "calculate": embedded_calculator}

# =====================================================================
# 📋 2. ReAct 灵魂 System Prompt（死锁格式天条）
# =====================================================================
REACT_SYSTEM_PROMPT = """
你是一个具备强大推理与行动能力的 AI 智能体（Agent）。
你有一套可以使用的工具箱，用于回答用户的复杂问题：
1. search(query): 传入查询词，返回维基百科的事实。
2. calculate(expression): 传入纯数学运算表达式，返回计算结果。

当用户提出问题时，你必须严格遵循以下格式进行逐步思考和行动，一次只能进行一个 Thought 和一个 Action：

Thought: 你当前正在思考什么，接下来打算干什么。
Action: 工具名[参数]（例如: search[苹果市值] 或 calculate[3.5 + 2.0]）

当外部系统执行完工具后，会把结果以 'Observation: 工具结果' 的形式喂给你。
你拿到 Observation 后，再次进行 Thought，直到你确信拿到了最终答案。
当你确认可以得出结论时，请输出以下最终格式：

Final Answer: 最终总结性的回答。

记住：每次你输出 Action 之后，必须立即停下来等待 Observation，绝对不能自己伪造 Observation！
"""


# =====================================================================
# ⚙️ 3. 核心 ReAct 状态机控制引擎
# =====================================================================
def run_react_agent(user_question: str, max_iterations: int = 5):
    print(f"👤 [用户复杂诉求] ❯ {user_question}\n")
    print("=" * 70)

    # 核心状态机历史
    messages = [
        {"role": "system", "content": REACT_SYSTEM_PROMPT},
        {"role": "user", "content": user_question},
    ]

    # 状态机循环
    for step in range(1, max_iterations + 1):
        print(f"🔄 [第 {step} 轮思考迭代]...")

        # 1. 呼叫大模型输出 Thought + Action
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            temperature=0.0,  # 必须用 0 度锁死逻辑确定性
            stop=[
                "Observation:"
            ],  # 🌟 强行设置停止词，防止大模型自己伪造 Observation 产生幻觉
        )

        llm_output = response.choices[0].message.content.strip()
        print(llm_output)

        # 将大模型本轮的思考和行动记录在案
        messages.append({"role": "assistant", "content": llm_output})

        # 2. 检查大模型是否已经给出了最终答案
        if "Final Answer:" in llm_output:
            final_match = llm_output.split("Final Answer:")[-1].strip()
            print("\n" + "=" * 50)
            print(f"🏆 [Agent 斩获最终答案] ❯")
            print(
                f"[bold green]{final_match}[/bold green]"
                if "rich" in sys.modules
                else final_match
            )
            print("=" * 50 + "\n")
            return

        # 3. 正则深度解构 Action
        # 匹配格式如：Action: search[苹果] 或 Action: calculate[3.5 + 2]
        action_pattern = r"Action:\s*(\w+)\[(.*?)\]"
        match = re.search(action_pattern, llm_output)

        if match:
            tool_name = match.group(1).strip()
            tool_arg = match.group(2).strip()

            print(
                f"\n⚙️ [物理拦截拦截器] ➡️ 检测到 Action 申请：调用 {tool_name}，参数: '{tool_arg}'"
            )

            # 4. 执行物理世界工具
            if tool_name in TOOL_BOX:
                tool_func = TOOL_BOX[tool_name]
                observation_result = tool_func(tool_arg)
            else:
                observation_result = f"Error: 工具 '{tool_name}' 不存在。"

            print(f"👁️ [Observation 回执] ➡️ {observation_result}\n")

            # 5. 将 Observation 作为新一轮输入塞回给大模型
            messages.append(
                {"role": "user", "content": f"Observation: {observation_result}"}
            )

        else:
            # 容灾分支：如果模型没有生成合规的 Action 格式，且也没有 Final Answer
            print("⚠️ [格式脱轨警告] 模型未生成合规 Action 格式，强行引导重新思考...")
            messages.append(
                {
                    "role": "user",
                    "content": "系统提示：你的 Action 格式不正确，请严格使用 'Action: 工具名[参数]' 格式重新输出。",
                }
            )

    # 熔断警报
    print(
        f"🛑 [强行熔断] 状态机已达到最大迭代上限 ({max_iterations} 次)，防止无限 Token 爆破死循环！"
    )


if __name__ == "__main__":
    # 复合型多步任务：先搜 A -> 再搜 B -> 本地数学计算
    complex_query = "帮我查询苹果公司和谷歌公司的市值总和是多少？"
    run_react_agent(complex_query, max_iterations=5)
