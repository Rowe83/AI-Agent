import os
from langchain_core.messages import trim_messages
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="deepseek-v4-flash", temperature=0.0, api_key=os.getenv("DEEPSEEK_API_KEY"), base_url=os.getenv("BASE_URL"))

# 定义消息裁剪器：仅保留最新 1000 个 Token 的消息，防止溢出
trimmer = trim_messages(
    max_tokens=1000,
    strategy="last",          # 保留最新消息
    token_counter=llm,        # 按照当前 LLM 模型的 Token 计算器计算
    include_system=True,      # 强制保留 SystemMessage
    allow_partial=False,
    start_on="human"          # 确保裁剪后的第一条消息是 User 消息
)

# 在 LCEL 中添加 trimmer 节点
chain_with_trimming = (
    RunnablePassthrough.assign(history=lambda x: trimmer.invoke(x["history"]))
    | prompt
    | model
)

# 包装为带历史的链
final_chain = RunnableWithMessageHistory(
    chain_with_trimming,
    get_session_history=get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)