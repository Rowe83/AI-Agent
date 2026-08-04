import os
import shutil
from typing import List
from dotenv import load_dotenv

# 1. 禁用 Chroma 自动遥测，防止网络超时挂起
os.environ["ANONYMIZED_TELEMETRY"] = "False"

load_dotenv()

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import ZhipuAIEmbeddings
from langchain_community.vectorstores import Chroma

# =====================================================================
# 🚀 1. 准备测试数据与格式化函数
# =====================================================================
raw_docs = [
    Document(
        page_content="NexusTech 公司规定：员工入职满 1 年享有 10 天带薪年假，试用期员工（前 3 个月）无带薪年假。",
        metadata={"source": "员工手册_HR_v2.pdf", "page": 12, "author": "HR部"},
    ),
    Document(
        page_content="NexusTech 公司的出差餐补标准为：一线城市（北京、上海、深圳）每天 250 元，二线城市每天 150 元。",
        metadata={"source": "财务报销规范_FIN_2026.pdf", "page": 5, "author": "财务部"},
    ),
    Document(
        page_content="每周五为公司 WFH（远程办公）开放日，需提前 24 小时在 OA 系统中报备。",
        metadata={"source": "员工手册_HR_v2.pdf", "page": 18, "author": "HR部"},
    ),
]


def format_docs_with_sources(docs: List[Document]) -> str:
    """
    格式化检索到的文档，将 Metadata 转化为结构化标记 [Doc i]，
    以便 LLM 在回答中进行精准角标引用。
    """
    formatted = []
    for idx, doc in enumerate(docs, start=1):
        source = doc.metadata.get("source", "未知来源")
        page = doc.metadata.get("page", "未知页码")
        formatted.append(
            f"[Doc {idx}] (出处: {source}, 第 {page} 页):\n{doc.page_content}"
        )
    return "\n\n".join(formatted)


# =====================================================================
# 📦 2. 初始化向量数据库与 Retriever (检索器)
# =====================================================================
DB_DIR = "./langchain_chroma_db"
if os.path.exists(DB_DIR):
    shutil.rmtree(DB_DIR)

# 使用智谱 Embedding-3
embeddings = ZhipuAIEmbeddings(model="embedding-3")

print("正在将文档向量化并建库...")
vectorstore = Chroma.from_documents(
    documents=raw_docs, embedding=embeddings, persist_directory=DB_DIR
)

# 转换为 Standard LangChain Retriever 检索器对象
retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

# =====================================================================
# 📝 3. 定义带 Source 引用的 Prompt Template
# =====================================================================
template = """系统指令：你是一个严谨的企业知识库助手。
请**严格依据**下方提供的 [参考文档] 回答用户的 [问题]。

【引用规则】：
1. 你的回答必须在句末标注信息来源的编号（例如：[Doc 1] 或 [Doc 2]）。
2. 如果参考文档没有提到相关答案，请直接回答：“根据已知文档，无法回答该问题。”，切勿捏造信息。

[参考文档]:
{context}

[用户问题]:
{question}
"""

prompt = ChatPromptTemplate.from_template(template)

# 初始化 LLM 模型
llm = ChatOpenAI(model=os.getenv("MODEL_NAME", "gpt-3.5-turbo"), temperature=0.0)

# =====================================================================
# 🔗 4. 构建 LCEL RAG 管道链
# =====================================================================
# 我们使用 RunnableParallel 既保留检索出来的原始 Document (拿来源)，又处理 Rag 管道
rag_chain_from_docs = (
    RunnablePassthrough.assign(
        context=(lambda x: format_docs_with_sources(x["context"]))
    )
    | prompt
    | llm
    | StrOutputParser()
)

# 完整的端到端 LCEL Chain
rag_chain_with_source = RunnableParallel(
    {"context": retriever, "question": RunnablePassthrough()}
).assign(answer=rag_chain_from_docs)

# =====================================================================
# 🧪 5. 运行验证：回答与出处标注
# =====================================================================
if __name__ == "__main__":
    test_query = "请问我在深圳出差 3 天，餐补标准是多少？试用期可以请年假吗？"

    print("\n" + "=" * 70)
    print(f"❓ 【提问】: {test_query}")
    print("=" * 70 + "\n")

    # 执行 LCEL 管道
    result = rag_chain_with_source.invoke(test_query)

    print(f"💡 【AI 回答 (带角标引用)】:\n{result['answer']}\n")

    print("📚 【引用的原始文档与 Metadata 追踪】:")
    for i, doc in enumerate(result["context"], start=1):
        print(
            f"  • [Doc {i}] 来源文件: {doc.metadata['source']} (第 {doc.metadata['page']} 页)"
        )
        print(f"    摘要内容: {doc.page_content[:40]}...")
 