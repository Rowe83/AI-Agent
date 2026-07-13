import os
import collections
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
# 注意：若使用 DeepSeek-R1 等原生自带思考链的模型，可直接请求；
# 这里我们用标准通用接口演示如何在代码层编排 Self-consistency 架构
client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=os.getenv("BASE_URL"))

# 💥 遭遇战目标：一段典型的 React/Vue 异步状态死锁与过时闭包 Bug 代码
TARGET_BUG_CODE = """
function UserProfile({ userId }) {
    const [user, setUser] = useState(null);
    useEffect(() => {
        // 隐患：未处理竞态条件(Race Condition)与闭包过时。
        // 如果 userId 在 50ms 内连续变动 3 次，最慢的那个老网络请求返回后会覆盖最新的数据！
        fetchUserData(userId).then(data => {
            setUser(data);
        });
    }, [userId]);
}
"""


def generate_single_cot_vote(sample_id: int) -> str:
    """单轨 CoT 推理采样"""
    prompt = f"""
你是一个顶级的前端 runtime 漏洞审计专家。请对以下代码进行深度像素级剖析。

[待审计代码]
{TARGET_BUG_CODE}

[任务说明]
请一步一步思考（Think step by step），分析此代码在极端高并发/快速切换状态下是否存在 Bug。
最后，你必须在回答的绝对末尾，换行输出一行最终裁决，格式严格为：【FINAL_VERDICT: BUG_EXISTED】或 【FINAL_VERDICT: SAFE】。

让我们一步一步开始深入思考：
"""
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,  # 🌟 必须开启温度，允许思考链产生不同的探索路径
            max_tokens=600,
        )
        content = response.choices[0].message.content
        print(f"🧬 [采样轨道 #{sample_id} 推理完成] 正在抽取局部结论...")
        return content
    except Exception as e:
        print(f"🛑 采样轨道 #{sample_id} 通信中断: {e}")
        return ""


def run_self_consistency_pipeline(sample_size: int = 3):
    print(f"🎬 启动自洽性采样流水线，采样规模: {sample_size} 路并发...")
    print("=" * 60)

    raw_outputs = []
    verdicts = []

    # 1. 采集多路样本（在真实高并发下，此处可用 asyncio.gather 提速）
    for i in range(sample_size):
        output = generate_single_cot_vote(sample_id=i + 1)
        if output:
            raw_outputs.append(output)

            # 2. 提取最终裁决标签
            if "FINAL_VERDICT: BUG_EXISTED" in output:
                verdicts.append("BUG_EXISTED")
            elif "FINAL_VERDICT: SAFE" in output:
                verdicts.append("SAFE")
            else:
                verdicts.append("UNKNOWN")

    print("\n" + "=" * 50)
    print("📊 【思维链多路合流审计看板】")
    print("=" * 50)
    for idx, verd in enumerate(verdicts):
        print(f"  - 采样轨道 #{idx+1} 判定结果 ➡️ {verd}")

    # 3. 核心大招：后端执行多路多数表决（Majority Vote）
    if not verdicts:
        print("🛑 全路网关熔断，无有效样本。")
        return

    counter = collections.Counter(verdicts)
    most_common_verdict, vote_count = counter.most_common(1)[0]
    confidence = (vote_count / len(verdicts)) * 100

    print("-" * 50)
    print(f"🏆 最终通过一致性决策判定: 【{most_common_verdict}】")
    print(f"🎯 架构置信度 (Confidence): {confidence:.1f}%")
    print("=" * 50)

    # 打印其中一条详细的 CoT 推理链路供开发人员 Review
    print("\n💡 [精选一条完整的 CoT 思考链回溯]：")
    print(raw_outputs[0])


if __name__ == "__main__":
    run_self_consistency_pipeline(sample_size=3)
