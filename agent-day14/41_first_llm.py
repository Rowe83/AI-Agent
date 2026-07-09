import os
import logging
from dotenv import load_dotenv
from openai import OpenAI

# 1. 启动日志审计
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] - %(message)s")

def initialize_llm_client() -> OpenAI:
    """
    安全加载环境变量，并初始化大模型标准 Client 实例
    """
    # 🌟 核心安全动作：从当前目录的 .env 文件中将变量注入到操作系统的 environ 中
    load_dotenv()
    
    # 动态安全提取
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("BASE_URL", "https://api.deepseek.com/v1")
    
    if not api_key:
        logging.critical("🛑 [配置崩溃] 发现未在 .env 中检测到合规的 API Key，系统启动中断！")
        raise ValueError("Missing API Key in environment.")
        
    logging.info(f"💾 环境变量注入成功。目标网关指向: {base_url}")
    
    # 初始化官方标准大模型 Client 句柄
    # 它会自动去吃系统的环境变量，但我们显式传入更具工程可控性
    client = OpenAI(api_key=api_key, base_url=base_url)
    return client


def invoke_first_llm_call(client: OpenAI) -> None:
    """
    向大模型发起标准的原子级多轮对话结构请求
    """
    logging.info("📡 正在组装异构报文，准备发射...")
    
    try:
        # 🌟 完美对齐现代 Agent 的多角色消息体数组
        # messages 是一个高内聚的字典列表，每个角色分工明确
        response = client.chat.completions.create(
            model="deepseek-chat", # 对应 DeepSeek-V3 统一标识，若用 OpenAI 可换成 gpt-4o
            messages=[
                # 🛠️ System: 规定模型的灵魂和人设（最高约束力）
                {"role": "system", "content": "你是一个严谨的资深前端架构师，说话冷酷、一针见血，只输出高内聚的干货。"},
                # 👤 User: 用户的真实请求
                {"role": "user", "content": "用 50 字以内解释为什么 React 19 的 Server Actions 改变了前后端通信格局。"}
            ],
            temperature=0.3,     # 🚀 降噪：控制创造力。0.3 代表追求高精准、确定性的技术输出
            max_tokens=150       # 🛡️ 熔断：强行锁死大模型最大能吐出的 Token 长度，防止额度暴扣
        )
        
    except Exception as e:
        logging.error(f"❌ [云端通信爆破] 遭遇厂商网关拦截或超时: {e}")
        return

    logging.info("🟢 报文成功安全回执！开始进行报文内容审计：")
    print("-" * 60)
    
    # 🌟 核心解构数据流（OpenAI 标准返回对象解构）
    # response.choices 是个列表，[0] 代表厂商给出的第一组最佳答案
    raw_message_obj = response.choices[0].message
    llm_reply_text = raw_message_obj.content
    
    print(f"🤖 LLM 架构师回复:\n{llm_reply_text}")
    print("-" * 60)
    
    # 📈 Token 审计：大模型会把本轮精准的开销带在 usage 字段里返回
    usage = response.usage
    if usage:
        print(f"📊 [Token 账单明细]：")
        print(f"  - 输入（Prompt Tokens）    : {usage.prompt_tokens}")
        print(f"  - 输出（Completion Tokens）: {usage.completion_tokens}")
        print(f"  - 本轮总共消耗 Tokens      : {usage.total_tokens}")
    print("-" * 60)


if __name__ == "__main__":
    print("🤖 初始化大模型一号总线...")
    try:
        ai_client = initialize_llm_client()
        invoke_first_llm_call(ai_client)
    except Exception as err:
        print(f"💥 启动遭遇致命硬熔断: {err}")