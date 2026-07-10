import os
import time
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=os.getenv("BASE_URL"))

# =====================================================================
# 💾 工业级静态本地示例库（包含不同的业务线）
# =====================================================================
EXAMPLE_POOL = [
    # 类别 A：性能问题
    {
        "query": "首页首屏白屏时间太长了，急死人",
        "reply": '{"category": "PERFORMANCE", "tier": "P0", "action": "LAZY_LOAD"}',
    },
    {
        "query": "长列表滚动的时候卡顿明显，有掉帧",
        "reply": '{"category": "PERFORMANCE", "tier": "P1", "action": "VIRTUAL_LIST"}',
    },
    # 类别 B：安全与鉴权问题
    {
        "query": "接口报错 403 越权访问，Token 似乎过期了",
        "reply": '{"category": "SECURITY", "tier": "P0", "action": "FORCE_LOGOUT"}',
    },
    {
        "query": "用户密码在网络传输中竟然是明文的，太危险了",
        "reply": '{"category": "SECURITY", "tier": "P0", "action": "ENCRYPT"}',
    },
    # 类别 C：UI/UX 体验问题
    {
        "query": "按钮的暗黑模式适配错了，字看不清",
        "reply": '{"category": "UI_UX", "tier": "P2", "action": "THEME_FIX"}',
    },
]


# =====================================================================
# 🛡️ 核心工程函数：动态示例挑选机制
# =====================================================================
def select_dynamic_examples(
    user_query: str, pool: List[Dict[str, str]], limit: int = 2
) -> List[Dict[str, str]]:
    """
    轻量级动态选择器：根据简单的核心关键词重合度进行动态匹配。
    (在真实的生产级 Agent 中，此处通常会使用 Embedding 向量相似度计算)
    """
    if limit == 0:
        return []

    keywords = ["白屏", "卡顿", "掉帧", "403", "Token", "密码", "明文", "暗黑", "按钮"]
    matched_words = [w for w in keywords if w in user_query]

    # 如果没有任何词匹配到，默认返回前几个
    if not matched_words:
        return pool[:limit]

    # 简单计分排序：谁包含的匹配词多谁排前面
    def score_example(item):
        return sum(1 for w in matched_words if w in item["query"])

    sorted_pool = sorted(pool, key=score_example, reverse=True)
    return sorted_pool[:limit]


# =====================================================================
# 📡 自动化评估总线
# =====================================================================
def run_few_shot_pipeline(user_input: str, shot_count: int):
    print(f"\n⚙️ [评估启动] 测试样本数量: {shot_count}-Shot")
    print("-" * 60)

    # 1. 动态捡漏，抽取最契合的锚点
    selected_shots = select_dynamic_examples(user_input, EXAMPLE_POOL, limit=shot_count)

    # 2. 动态组装 Prompt 结构体
    prompt_builder = "你是一个自动化前端运维监控 Agent。请将用户的线上故障报修文本，分类清洗为标准的 JSON 字典。\n\n"

    # 循环把选出来的例子塞进上下文
    for i, shot in enumerate(selected_shots):
        prompt_builder += f"[示例 {i+1}]\n"
        prompt_builder += f"输入：{shot['query']}\n"
        prompt_builder += f"输出：{shot['reply']}\n\n"

    prompt_builder += "[最新目标]\n"
    prompt_builder += f"输入：{user_input}\n"
    prompt_builder += "输出："

    # 3. 发射网关
    t0 = time.time()
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt_builder}],
            temperature=0.0,
            response_format={"type": "json_object"},  # 强制拉起底层 JSON 拦截
        )
        latency = time.time() - t0
        print(f"⏱️ 响应延迟: {latency:.2f} 秒")
        print(f"🤖 LLM 返回报文:\n{response.choices[0].message.content}")
    except Exception as e:
        print(f"🛑 熔断崩溃: {e}")
    print("=" * 60)


if __name__ == "__main__":
    # 💥 测试用例：传入一个包含鉴权（403）和 Token 相关的复合安全故障
    test_query = (
        "后台管理系统突然大面积报 403 权限拒绝，疑似安全证书或 Token 校验链挂了"
    )

    print(f"🔍 线上真实故障录入: '{test_query}'")
    print("*" * 60)

    # 对抗运行 A：0-Shot（不给任何参考例子，看大模型自由发挥的字段命名）
    run_few_shot_pipeline(test_query, shot_count=0)

    # 对抗运行 B：2-Shot（带动态选择，系统会自动挑选出包含 '403'、'Token' 等安全相关的最佳锚点注入）
    run_few_shot_pipeline(test_query, shot_count=2)
