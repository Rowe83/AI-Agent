import os
import json
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma

# =====================================================================
# 🛠️ 1. 模型组件初始化 (部署测试对象与裁判 LLM)
# =====================================================================
zhipu_embeddings = OpenAIEmbeddings(
    model="embedding-3",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
    base_url=os.getenv("ZHIPU_BASE_URL")
)

rag_llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    temperature=0.0
)

judge_llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    temperature=0.0
)

# =====================================================================
# 📦 2. 准备底稿知识库并建立检索器
# =====================================================================
raw_knowledge_base = [
    Document(page_content="NexusTech 公司规定：试用期员工（前 3 个月）无带薪年假，入职满 1 年享有 10 天带薪年假。", metadata={"source": "员工手册_HR_v2.pdf"}),
    Document(page_content="NexusTech 出差餐补：一线城市（北京、上海、深圳）每天 250 元，二线城市每天 150 元。报销需在回程后 5 个工作日内提交 OA。", metadata={"source": "财务报销规范_FIN_2026.pdf"}),
    Document(page_content="每周五为公司 WFH（居家办公）开放日，员工需提前 24 小时在 OA 系统中提交申请并获得主管批准。", metadata={"source": "员工手册_HR_v2.pdf"}),
    Document(page_content="针对 P1 级系统故障，技术支持团队必须在 15 分钟内响应并开始排查；P2 级故障需在 30 分钟内响应。", metadata={"source": "运维服务等级协议_SLA.pdf"}),
    Document(page_content="NX-9000 Pro 产品参数：最大支持带宽为 100 Gbps，硬件质保期为 3 年，提供 7x24 小时技术服务支持。", metadata={"source": "产品规格说明书_2026.pdf"})
]

vectorstores = Chroma.from_documents(documents=raw_knowledge_base, embedding=zhipu_embeddings)
retriever = vectorstores.as_retriever(search_kwargs={"k": 2})

# =====================================================================
# 🔗 3. 待测试的标准 RAG Pipeline 运行逻辑
# =====================================================================
rag_prompt = ChatPromptTemplate.from_template(
    "根据以下提供的参考文档，严格回答用户的问题。如果无法回答，请说不知道。\n\n"
    "[参考文档]:\n{context}\n\n"
    "[用户问题]:\n{question}"
)

def run_rag_pipline(question: str) -> Dict:
    retrieved_docs = retriever.invoke(question)
    context_str = "\n".join([doc.page_content for doc in retrieved_docs])

    chain = rag_prompt | rag_llm | StrOutputParser()
    answer = chain.invoke({"context": context_str, "question": question})

    return {
        "question": question,
        "context": [doc.page_content for doc in retrieved_docs],
        "answer": answer
    }

# =====================================================================
# ⚖️ 4. 构建 LLM-as-a-Judge 评估器 (计算 Faithfulness & Correctness)
# =====================================================================

# 忠实度 (Faithfulness) 评估 Prompt：检查 Answer 中的论断是否全部来源于 Contexts
faithfulness_prompt = ChatPromptTemplate.from_template(
    "你是一个严格的文档逻辑审计员。\n"
    "请判断【AI回答】中的观点是否完全可以由【参考上下文】推导出来，不要混入任何外部知识。\n"
    "请给出0 到 100 之间的忠实度分数（只输出纯数字分数）。\n"
    "【参考上下文】:\n{context}\n\n"
    "【AI回答】:\n{answer}\n\n"
    "忠实度分数（0-100）："
)

# 准确度 (Correctness) 评估 Prompt：检查 AI回答 与 标准答案 是否一致
correctness_prompt = ChatPromptTemplate.from_template(
    "你是一个事实对比专家。\n"
    "请对比【AI回答】与【标准答案】，评估 AI 回答的事实准确性和完整度。\n"
    "请给出 0 到 100 之间的准确度分数（只输出纯数字分数）。\n\n"
    "【标准答案】:\n{ground_truth}\n\n"
    "【AI回答】:\n{answer}\n\n"
    "得分 (0-100):"
)

faithfulness_chain = faithfulness_prompt | judge_llm | StrOutputParser()
correctness_chain = correctness_prompt | judge_llm | StrOutputParser()

def evaluate_single_case(rag_result: Dict, ground_truth: str) -> Dict:
    context_str = "\n".join(rag_result["context"])
    answer = rag_result["answer"]

    try:
        f_score_str = faithfulness_chain.invoke({"context": context_str, "answer": answer})
        faithfulness_score = float(f_score_str.strip())
    except Exception:
        faithfulness_score = 0.0

    try:
        c_score_str = correctness_chain.invoke({"ground_truth": ground_truth, "answer": answer})
        correctness_score = float(c_score_str.strip())
    except Exception:
        correctness_score = 0.0

    return {
        "faithfulness_score": faithfulness_score,
        "correctness_score": correctness_score
    }

# =====================================================================
# 🚀 5. 执行批量评估与诊断生成
# =====================================================================
if __name__ == "__main__":
    # 导入预先定义的测试数据集 (取前 5 条作为示例运行)
    test_suite = [
        {
            "question": "NexusTech 公司员工试用期有带薪年假吗？",
            "ground_truth": "试用期员工无带薪年假，入职满1年享有10天带薪年假。"
        },
        {
            "question": "在一线城市出差的餐补标准是每天多少钱？",
            "ground_truth": "在一线城市（北京、上海、深圳）出差，餐补标准为每天250元。"
        },
        {
            "question": "针对 P1 级系统故障，技术支持团队的响应时间要求是多少？",
            "ground_truth": "针对 P1 级系统故障，技术支持团队必须在 15 分钟内响应。"
        },
        {
            "question": "NX-9000 Pro 的硬件质保期是几年？",
            "ground_truth": "NX-9000 Pro 的硬件质保期为 3 年。"
        },
        {
            "question": "出差差旅费报销需要在回程后多少天内提交？",
            "ground_truth": "差旅报销需在出差结束后 5 个工作日内提交 OA。"
        }
    ]

    print("📊 开始执行 RAG Pipeline 自动化评估...\n")

    total_faithfulness = 0.0
    total_correctness = 0.0

    for idx, test_case in enumerate(test_suite, 1):
        q = test_case["question"]
        gt = test_case["ground_truth"]

        # 1. 运行 RAG 拿到实际回答
        rag_out = run_rag_pipline(q)

        # 2. 评估打分
        eval_res = evaluate_single_case(rag_out, gt)

        eval_f_score = eval_res["faithfulness_score"]
        eval_c_score = eval_res["correctness_score"]

        total_faithfulness += eval_f_score
        total_correctness += eval_c_score

        print(f" Test Case [{idx}]: {q}")
        print(f"  🤖 AI 回答:  {rag_out['answer']}")
        print(f"  🎯 标准答案: {gt}")
        print(f"  📈 忠实度 (Faithfulness): {eval_f_score} | 准确度 (Correctness): {eval_c_score}")
        print("-" * 70)

    avg_faithfulness = total_faithfulness / len(test_suite)
    avg_correctness = total_correctness / len(test_suite)

    print("\n" + "="*70)
    print("🏆 【RAG 系统总健康度评估报告】")
    print(f"  • 平均忠实度得分 (Faithfulness): {avg_faithfulness:.2f} / 100")
    print(f"  • 平均准确度得分 (Correctness):  {avg_correctness:.2f} / 100")
    print("="*70)