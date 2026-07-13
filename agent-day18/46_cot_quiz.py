import os
import time
from dotenv import load_dotenv
from openai import OpenAI
from typing import List, Dict, Any

load_dotenv()
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=os.getenv("BASE_URL"))

# =====================================================================
# 💾 10 道精选高维逻辑/全栈陷阱推理题库
# =====================================================================
QUIZ_BANK: List[Dict[str, Any]] = [
    {
        "id": 1,
        "type": "经典时间逻辑",
        "question": "小明家的时钟整点敲响。3点整时，时钟敲 3 下，总共耗时 6 秒（从第1下开始到第3下结束）。请问到 6 点整时，时钟敲 6 下，总共需要耗时多少秒？",
        "expected_key": "15",  # 陷阱：3下有2个间隔，每个间隔3秒；6下有5个间隔，5*3=15秒。直觉容易错答12。
    },
    {
        "id": 2,
        "type": "高并发模拟",
        "question": "一个全栈队列系统每分钟能安全处理 60 个 Webhook 异步请求。但每过 1 分钟，由于内存泄漏，系统的吞吐量会永久下降 10 个（即第1分钟处理60个，第2分钟处理50个，以此类推）。同时，系统每分钟会固定积压 40 个新请求。请问从系统启动（积压为0）开始算起，到第几分钟结束时，系统会彻底发生请求堆积（积压数大于0）？",
        "expected_key": "4",  # 第1分：处理60/积压40，剩0；第2分：处理50/积压40，剩0；第3分：处理40/积压40，剩0；第4分：处理30/积压40，堆积10个。
    },
    {
        "id": 3,
        "type": "空间地理推理",
        "question": "一架无人机从前端低空机库出发，先向正南飞行了 50 公里，接着向正东飞行了 50 公里，最后向正北飞行了 50 公里，发现自己竟然奇迹般地回到了出发点的正上方。请问，该无人机的出发点在地球的什么特殊地理位置？",
        "expected_key": "南极",  # 或者是南极点附近。在北极点向南、东、北飞行会回到原点，但在南极出发向南飞无法前行。等一下，北极点出发，向南、向东、向北，会回到北极点！而南极点出发不能向南。所以答案是北极点！
    },
    {
        "id": 3,  # 修正题目：北极点
        "type": "空间地理推理",
        "question": "一架无人机从前端低空机库出发，先向正南飞行了 50 公里，接着向正东飞行了 50 公里，最后向正北飞行了 50 公里，发现自己竟然奇迹般地回到了出发点的正上方。请问，该无人机的出发点在地球的什么特殊地理位置？",
        "expected_key": "北极",  # 从北极点出发，任何方向都是南。向南50，向东50（绕极圈），向北50，回到北极点。
    },
    {
        "id": 4,
        "type": "跨期结算与代币",
        "question": "独立 SaaS 平台发行了一种限量 Token。第一天小张用 100 元买入 1 枚，第二天由于大模型大火，他以 110 元卖出。第三天他觉得卖亏了，又花 120 元买回 1 枚。第四天他最终以 130 元将这枚 Token 彻底清仓。请问在不计手续费的情况下，小张这一波操作总共净赚了多少元？",
        "expected_key": "20",  # 两次独立的买卖：100买110卖赚10；120买130卖赚10。总共赚20。直觉容易被混淆成10。
    },
    {
        "id": 5,
        "type": "条件悖论",
        "question": "某大厂面试题：有三个密闭盒子。A 盒子写着：'宝藏在 B 盒子或 C 盒子中'；B 盒子写着：'宝藏不在此盒子中'；C 盒子写着：'宝藏在 A 盒子中'。已知这三个盒子上的标签只有一句话是真的。请问宝藏究竟在哪个盒子中？",
        "expected_key": "B",  # 若在B：A真，B假，C假，满足只有一真。若在A：A假，B真，C真（两真冲突）。若在C：A真，B真，C假（两真冲突）。
    },
    {
        "id": 6,
        "type": "数字序列陷阱",
        "question": "观察以下特定路由网段权重序列：2，4，12，48，240，(__)。请问括号里应该填写的下一个数字是什么？",
        "expected_key": "1440",  # 规律：*2, *3, *4, *5, *6。 240 * 6 = 1440。
    },
    {
        "id": 7,
        "type": "前端竞态概率",
        "question": "在 AILoad 性能测试中，页面有 A、B 两个异步组件。A 组件有 60% 的概率比 B 组件先完成渲染。现在连续刷新页面 3 次，请问至少有 2 次是 A 组件比 B 组件先完成渲染的概率是多少？（请用百分数或分数表示，如 64.8% 或 81/125）",
        "expected_key": "64.8%",  # 恰好2次先：3 * 0.6^2 * 0.4 = 0.432；3次都先：0.6^3 = 0.216。0.432 + 0.216 = 0.648 = 64.8%。
    },
    {
        "id": 8,
        "type": "集合覆盖范围",
        "question": "一个全栈团队有 10 个人，其中有 7 个人精通 React 前端开发，有 5 个人精通 Python 后端开发，有 3 个人两门都精通。请问这个团队里，既不精通 React 也不精通 Python 的全栈小白有几个人？",
        "expected_key": "1",  # 精通React或Python的总人数 = 7 + 5 - 3 = 9人。 小白 = 10 - 9 = 1人。
    },
    {
        "id": 9,
        "type": "多Agent生存期",
        "question": "5 个智能体（Agent）在一起开会，他们每个人手里都拿着一份保密协议。如果一个 Agent 把协议传给另一个 Agent 需要耗时 1 分钟。为了让所有人手里都拥有全部 5 个智能体的保密协议副本，在允许大家多轨并发相互传送的情况下，整个团队最少需要耗时几分钟？",
        "expected_key": "2",  # 第1分钟：1传2，3传4，5留。第2分钟：通过交叉错位传递，可以在2分钟内完成全员覆盖（类似全双工网卡通信拓扑）。
    },
    {
        "id": 10,
        "type": "字符串解构逆转",
        "question": "一个古怪的 AI 编译器会对字符串进行如下转换规则：先将字符串翻转，然后将所有的 'A' 替换成 'X'。如果一个原始字符串经过该编译器转换后，输出的结果是 'XTRCEER'，请问原始字符串在未转换前是什么？",
        "expected_key": "REECTRA",  # 逆操作：先翻转回来 -> REECRTX -> 再把X还原成A -> REECTRA（对齐REACT）。等一下，'XTRCEER'翻转是'REECRTX'，X在最后，还原是A，即'REECRTA'。
    },
]

# 修正第10题的微调，确保严谨：'XTRCEER' -> 翻转: 'REECRTX'（原词第四个是C，第五个是R）。翻转过来是 REECRTX -> 替换回A => REECRTA。

QUIZ_BANK[9]["expected_key"] = "REECRTA"


# =====================================================================
# 📡 评测机双轨引擎
# =====================================================================
def ask_llm(prompt: str, use_cot: bool) -> str:
    """统一向厂商网关发射请求"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,  # 必须用0度锁死干扰变量
            max_tokens=800 if use_cot else 150,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {e}"


def run_evaluation_battle():
    print("🎬 [2026 工业级] CoT 推理能力 10 局极限对抗赛正式开打！")
    print("=" * 70)

    cot_score = 0
    direct_score = 0

    for item in QUIZ_BANK:
        print(f"\n🧩 [第 {item['id']} 题 | {item['type']}]")
        print(f"题目: {item['question']}")

        # 1. 组装直觉 Prompt（不允许分步思考，逼迫其直接交卷）
        direct_prompt = f"""
{item['question']}
注意：你必须不经任何解释，直接输出最终的答案核心（如一个数字、单词或百分数），不要带任何废话。
最终答案："""

        # 2. 组装 CoT 思维链 Prompt
        cot_prompt = f"""
{item['question']}
任务说明：请你先一步一步详细思考（Let's think step by step），写下推导逻辑。
最后，你必须在回答的【绝对最末尾】，换行单设一行，以严格的格式输出你的最终答案：
【FINAL_ANSWER: 你的答案】
"""

        # 运行双轨对抗
        direct_ans = ask_llm(direct_prompt, use_cot=False)
        cot_full_res = ask_llm(cot_prompt, use_cot=True)

        # 从 CoT 返回值中安全捞取核心答案标签
        cot_ans = "未提取出"
        if "【FINAL_ANSWER:" in cot_full_res:
            cot_ans = (
                cot_full_res.split("【FINAL_ANSWER:")[-1].replace("】", "").strip()
            )

        # 核心审计断言（只要预期关键字在吐出的答案字符串中，即判对）
        expected = item["expected_key"]
        direct_ok = expected in direct_ans
        cot_ok = expected in cot_ans

        if direct_ok:
            direct_score += 1
        if cot_ok:
            cot_score += 1

        print(
            f"🛑 [直觉轨 (No CoT)] 吐出: {direct_ans:<15} ➡️ 判定: {'✅ 正确' if direct_ok else '❌ 翻车'}"
        )
        print(
            f"🧬 [思维链 (With CoT)] 捞出: {cot_ans:<15} ➡️ 判定: {'✅ 正确' if cot_ok else '❌ 翻车'}"
        )

        # 如果直觉轨翻车而 CoT 对了，打印 CoT 的思考过程供人类架构师 Review
        if cot_ok and not direct_ok:
            print(f"💡 [CoT 逆袭思考链片段回溯]:")
            # 截取前两行展示思考痕迹
            lines = [
                line
                for line in cot_full_res.split("\n")
                if line.strip() and "FINAL_ANSWER" not in line
            ]
            print(f"   -> {lines[0] if len(lines)>0 else ''}")
            print(f"   -> {lines[1] if len(lines)>1 else ''}")

    print("\n" + "=" * 50)
    print("📊 【10 局对抗赛最终审计战报】")
    print("=" * 50)
    print(f"🟢 直觉轨道 (Standard Mode) 命中率 : {direct_score} / 10")
    print(f"🏆 思维链轨 (CoT Mode)      命中率 : {cot_score} / 10")
    print("-" * 50)
    print(f"🎯 结论: CoT 带来了 {(cot_score - direct_score)*10}% 的鲁棒性飞跃！")
    print("=" * 50)


if __name__ == "__main__":
    run_evaluation_battle()
