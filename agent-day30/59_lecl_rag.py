import os
import shutil
from typing import List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma

# =====================================================================
# 🛠️ 1. 初始化智谱 embedding-3 与 DeepSeek 模型组件
# =====================================================================

# 智谱 embedding-3 向量模型 (兼容 OpenAI 规范接口)
zhipu_embeddings = OpenAIEmbeddings(
    model="embedding-3",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
    base_url=os.getenv("ZHIPU_BASE_URL"),
)

# DeepSeek-v4-flash 大语言模型
deepseek_llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    temperature=0.0,
)

# =====================================================================
# 📦 2. 准备带 Metadata 属性的知识库文档与向量库建库
# =====================================================================
raw_docs = [
    Document(
        page_content="NexusTech 公司规定：员工入职满 1 年享有 10 天带薪年假，试用期员工（前 3 个月）无带薪年假。",
        metadata={"source": "员工手册_HR_v2.pdf", "page": 12},
    ),
    Document(
        page_content="NexusTech 公司的出差餐补标准为：一线城市（北京、上海、深圳）每天 250 元，二线城市每天 150 元。",
        metadata={"source": "财务报销规范_FIN_2026.pdf", "page": 5},
    ),
    Document(
        page_content="每周五为公司 WFH（远程办公）开放日，员工需提前 24 小时在 OA 系统中提交申请并获得主管批准。",
        metadata={"source": "员工手册_HR_v2.pdf", "page": 18},
    ),
]

DB_DIR = "./zhipu_chroma_db"
if os.path.exists(DB_DIR):
    shutil.rmtree(DB_DIR)

print("🚀 正在调用智谱 embedding-3 生成向量并构建 Chroma 向量库...")
vectorstore = Chroma.from_documents(
    documents=raw_docs, embedding=zhipu_embeddings, persist_directory=DB_DIR
)

# 转换为 LCEL 标准检索器，检索 Top-2 相关文档
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# =====================================================================
# 📝 3. 定义格式化函数与带引用约束的 Prompt 模板
# =====================================================================


def format_docs_with_sources(docs: List[Document]) -> str:
    """
    将检索出的 Document 转换为 [Doc 1], [Doc 2] 编号格式，
    将文件来源 (source) 和页码 (page) 拼接到上下文供 LLM 引用。
    """
    formatted = []
    for idx, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "未知来源")
        page = doc.metadata.get("page", "未知页码")
        formatted.append(
            f"[Doc {idx}] (出处: {source}, 第 {page} 页):\n{doc.page_content}"
        )
    return "\n\n".join(formatted)


template = """系统指令：你是一个严谨的企业知识库助手。
请**严格依据**下方提供的 [参考文档] 回答用户的 [问题]。

【引用与回答规则】：
1. 你的回答必须在句末关键信息后标注引用的文档编号（例如：[Doc 1] 或 [Doc 2]）。
2. 如果参考文档中没有提到的内容，请直接回答：“根据已知文档，无法回答该问题。”，绝对不能编造。

[参考文档]:
{context}

[用户问题]:
{question}
"""

prompt = ChatPromptTemplate.from_template(template)

# =====================================================================
# 🔗 4. 构建 LCEL 管道链 (智谱 Embeddings + DeepSeek LLM)
# =====================================================================

# 核心 RAG 处理流水线
# 数据流: {"context": ..., "question": ...} -> Prompt -> DeepSeek -> 解析纯文本
rag_chain_from_docs = (
    RunnablePassthrough.assign(context=lambda x: format_docs_with_sources(x["context"]))
    | prompt
    | deepseek_llm
    | StrOutputParser()
)

# 完整端到端管道：并行获取检索文档 (Retriever) 与保存原始提问 (Question)
rag_chain_with_source = RunnableParallel(
    {"context": retriever, "question": RunnablePassthrough()}
).assign(answer=rag_chain_from_docs)

# =====================================================================
# 🧪 5. 执行测试与结果打印
# =====================================================================
if __name__ == "__main__":
    test_query = "请问我在深圳出差 3 天，餐补标准是多少？试用期可以请年假吗？"

    print("\n" + "=" * 70)
    print(f"❓ 【提问】: {test_query}")
    print("=" * 70 + "\n")

    # 执行 LCEL 管道
    result = rag_chain_with_source.invoke(test_query)

    print(f"💡 【DeepSeek 回答 (带角标引用)】:\n{result['answer']}\n")

    print("📚 【智谱 Embedding 检索到的底稿源追踪】:")
    for i, doc in enumerate(result["context"], start=1):
        print(
            f"  • [Doc {i}] 来源: {doc.metadata['source']} (第 {doc.metadata['page']} 页)"
        )
        print(f"    内容: {doc.page_content}")
