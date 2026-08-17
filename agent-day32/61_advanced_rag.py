import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 初始化模型
zhipu_embeddings = OpenAIEmbeddings(
    model="embedding-3",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
    base_url=os.getenv("ZHIPU_BASE_URL"),
)

deepseek_llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
)

# =====================================================================
# 📦 2. 准备数据集与基础检索器构建
# =====================================================================
raw_docs = [
    Document(
        page_content="NexusTech 的出差餐补标准：一线城市（北京、上海、深圳）每天 250 元，二线城市每天 150 元。",
        metadata={"id": "doc1"},
    ),
    Document(
        page_content="NexusTech 公司员工福利指南：入职满 1 年享有 10 天带薪年假，试用期（前 3 个月）无带薪年假。",
        metadata={"id": "doc2"},
    ),
    Document(
        page_content="NexusTech 运维响应等级：针对 P1 级系统故障，技术支持团队必须在 15 分钟内响应并开始排查。",
        metadata={"id": "doc3"},
    ),
    Document(
        page_content="关于 WFH 居家办公说明：每周五为开放日，需提前 24 小时在系统申请并获得主管批准。",
        metadata={"id": "doc4"},
    ),
]

# 2.1 向量检索器 (Dense)
vectorstore = Chroma.from_documents(documents=raw_docs, embedding=zhipu_embeddings)
dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 2.2 BM25 关键词检索器 (Sparse)
sparse_retriever = BM25Retriever.from_documents(documents=raw_docs)
sparse_retriever.k = 3


# =====================================================================
# 🔀 3. 算法实现：RRF (Reciprocal Rank Fusion) 倒数排名融合
# =====================================================================
def rrf_fusion(results_list: List[List[Document]], k: int = 60) -> List[Document]:
    """
    RRF 算法实现：融合向量检索与关键词检索的多个排序列表
    """
    doc_scores: Dict[str, float] = {}
    doc_map: Dict[str, Document] = {}

    for docs in results_list:
        for rank, doc in enumerate(docs, start=1):
            doc_id = doc.page_content  # 使用文本作为唯一标识
            doc_map[doc_id] = doc
            if doc_id not in doc_scores:
                doc_scores[doc_id] = 0.0
            doc_scores[doc_id] += 1.0 / (k + rank)

    # 按照 RRF 累加得分从高到低排序
    sorted_docs = sorted(doc_scores.items(), key=lambda item: item[1], reverse=True)
    return [doc_map[doc_id] for doc_id, _ in sorted_docs]


# =====================================================================
# 🔄 4. 查询改写：Multi-Query 扩展
# =====================================================================
multi_query_prompt = ChatPromptTemplate.from_template(
    "你是一个 AI 搜索助手。请针对用户的原始提问，生成 3 个不同角度的改写版本，用于提高检索召回率。\n"
    "每行输出一个改写后的提问，不要包含任何编号或多余文本。\n"
    "原始提问: {question}"
)

multi_query_chain = multi_query_prompt | deepseek_llm | StrOutputParser()


def generate_multi_queries(original_query: str) -> List[str]:
    raw_output = multi_query_chain.invoke({"question": original_query})
    queries = [q.strip() for q in raw_output.strip().split("\n") if q.strip()]
    return [original_query] + queries[:3]  # 返回原始提问 + 3 个改写提问


# =====================================================================
# 🎯 5. 极简 Cross-Encoder 重排序逻辑 (Reranker)
# =====================================================================
rerank_prompt = ChatPromptTemplate.from_template(
    "评估以下【参考文档】与【用户问题】的相关性，请打出 0 到 100 之间的分数（仅输出数字）。\n"
    "问题: {question}\n"
    "文档: {doc_content}\n"
    "分数:"
)
rerank_chain = rerank_prompt | deepseek_llm | StrOutputParser()


def rerank_documents(
    query: str, docs: List[Document], top_n: int = 2
) -> List[Document]:
    """
    对召回的文档列表进行 LLM-based Rerank 重排序
    """
    scored_docs = []
    for doc in docs:
        try:
            score_str = rerank_chain.invoke(
                {"question": query, "doc_content": doc.page_content}
            )
            score = float(score_str.strip())
        except Exception:
            score = 0.0
        scored_docs.append((doc, score))

    # 按重排得分从高到低降序排列，截取 Top-N
    scored_docs.sort(key=lambda x: x[1], reverse=True)
    return [doc for doc, score in scored_docs[:top_n]]


# =====================================================================
# 📏 6. 检索评估工具函数 (Hit Rate & MRR)
# =====================================================================
def evaluate_retrieval(retrieved_docs: List[Document], ground_truth_id: str):
    """
    计算 Hits@K 与 MRR 得分
    """
    hit = 0
    mrr = 0.0
    for rank, doc in enumerate(retrieved_docs, start=1):
        if doc.metadata.get("id") == ground_truth_id:
            hit = 1
            mrr = 1.0 / rank
            break
    return hit, mrr


# =====================================================================
# 🚀 7. 运行端到端高级检索 Pipeline
# =====================================================================
if __name__ == "__main__":
    user_query = "紧急情况，P1级系统故障几分钟内要响应？"
    ground_truth = "doc3"  # 正确的目标文档 ID

    print("=" * 70)
    print(f"❓ 【原始提问】: {user_query}")
    print("=" * 70)

    # 1. 执行 Multi-Query 查询扩展
    expanded_queries = generate_multi_queries(user_query)
    print("\n🔍 【Multi-Query 扩展生成的查询视角】:")
    for i, q in enumerate(expanded_queries):
        print(f"  {i+1}. {q}")

    # 2. 对每个扩展 Query 执行（向量 + BM25）混合检索
    all_retrieved_lists = []
    for q in expanded_queries:
        dense_res = dense_retriever.invoke(q)
        sparse_res = sparse_retriever.invoke(q)
        all_retrieved_lists.append(dense_res)
        all_retrieved_lists.append(sparse_res)

    # 3. 使用 RRF 融合去重 (粗筛，召回前 4 篇)
    fused_docs = rrf_fusion(all_retrieved_lists)[:4]
    print(f"\n🔀 【RRF 融合检索召回文档数】: {len(fused_docs)} 篇")

    # 4. 执行 Reranker 重排序 (精筛，选前 2 篇)
    final_docs = rerank_documents(user_query, fused_docs, top_n=2)

    print("\n🏆 【Rerank 重排序后精选最终文档】:")
    for i, doc in enumerate(final_docs, start=1):
        print(f"  [{i}] Doc ID: {doc.metadata['id']} | 内容: {doc.page_content}")

    # 5. 计算评估指标
    hit, mrr = evaluate_retrieval(final_docs, ground_truth)
    print("\n📊 【检索效果评估报告】:")
    print(f"  • Hit Rate @ 2: {hit}")
    print(f"  • MRR 得分:     {mrr:.4f}")
