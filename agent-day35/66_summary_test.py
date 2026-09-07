import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_openai import ChatOpenAI

load_dotenv()

# 1. 模型初始化 (请根据实际环境配置 API Key 与 Base URL)
llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    temperature=0.3
)

# 2. 定义 Prompt 模板与单步子链

# --- Step 1: 提炼摘要 ---
summary_prompt = ChatPromptTemplate.from_template(
    "请对以下长文本进行提炼，生成一段不超过 100 字的核心摘要：\n\n{original_text}"
)
summary_chain = summary_prompt | llm | StrOutputParser()

# --- Step 2: 语言翻译 ---
translate_prompt = ChatPromptTemplate.from_template(
    "请将以下文本翻译为 {target_language}，保持意思准确：\n\n{summary}"
)
translate_chain = translate_prompt | llm | StrOutputParser()

# --- Step 3: 地道润色 ---
polish_prompt = ChatPromptTemplate.from_template(
    "你是一位资深编辑。请对以下 {target_language} 文本进行润色与修饰，使其更加地道、专业且优美：\n\n{draft_translation}"
)
polish_chain = polish_prompt | llm | StrOutputParser()

# 3. 构造自定义 Python Transform 节点（数据清洗/日志打印）
def log_step(data: dict) -> dict:
    print(f"--> [中间状态检查] 当前已生成步骤: {list(data.keys())}")
    return data

logger_node = RunnableLambda(log_step)

# 4. 使用 LCEL 串联三步骤管道
# 通过 RunnablePassthrough.assign 逐步叠加 key，避免变量丢失
pipeline = (
    # 步骤 1: 生成 summary
    RunnablePassthrough.assign(summary=summary_chain)
    | logger_node
    # 步骤 2: 生成 draft_translation (依赖 summary 和 target_language)
    | RunnablePassthrough.assign(draft_translation=translate_chain)
    | logger_node
    # 步骤 3: 生成 polished_result (依赖 draft_translation 和 target_language)
    | RunnablePassthrough.assign(polished_result=polish_chain)
)

# 5. 测试运行
if __name__ == "__main__":
    article_text = """
    人工智能驱动的自动化技术正迅速改变全球软件开发范式。
    传统的代码编写正从完全人工手动撰写，过渡到由智能体协同完成辅助重构、测试用例生成以及自动化部署。
    开发者的角色正在由纯粹的行代码编写者，转变为高层级系统架构的设计者与 AI 智能体的工作流管理者。
    这一深刻变革大幅降低了软件工程的构建门槛，同时也对开发者的系统性思维和全局掌控力提出了全新的挑战。
    """

    input_payload = {
        "original_text": article_text,
        "target_language": "英文"
    }

    print("🚀 开始运行【摘要 -> 翻译 -> 润色】串联链...\n")
    output = pipeline.invoke(input_payload)

    print("\n" + "="*50)
    print("📌 运行结果汇总：")
    print("="*50)
    print(f"【1. 原始文本片段】:\n{output['original_text'].strip()[:60]}...\n")
    print(f"【2. 核心摘要】:\n{output['summary']}\n")
    print(f"【3. 初翻译稿 ({output['target_language']})】:\n{output['draft_translation']}\n")
    print(f"【4. 润色终稿 ({output['target_language']})】:\n{output['polished_result']}")
    print("="*50)