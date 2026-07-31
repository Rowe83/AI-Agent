import os
import shutil
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量 (OPENAI_API_KEY, OPENAI_BASE_URL)
load_dotenv()


# =====================================================================
# 📦 1. 封装完整的 RAG Pipeline 引擎
# =====================================================================
class BasicRAGPipeline:
    def __init__(self, db_path="./chroma_rag_db", collection_name="company_kb"):
        self.db_path = db_path
        self.collection_name = collection_name

        # 初始化 OpenAI API 客户端
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("DEEPSEEK_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        if not api_key:
            raise ValueError("请在 .env 中配置 OPENAI_API_KEY！")
        self.llm_client = OpenAI(api_key=api_key, base_url=base_url)

        # 初始化 ChromaDB 客户端
        self.chroma_client = chromadb.PersistentClient(path=self.db_path)

        # 获取或创建 Collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.collection_name, metadata={"hnsw:space": "cosine"}
        )

    def _get_embedding(self, text: str) -> list:
        """调用 API 生成文本向量"""
        response = self.llm_client.embeddings.create(
            model="text-embedding-3-small", input=text
        )
        return response.data[0].embedding

    def build_knowledge_base(self, documents: list[str], metadatas: list[dict]):
        """【离线索引】切分、向量化并存储文档库"""
        print(f"正在将 {len(documents)} 条文档切分并存入 ChromaDB 向量库...")
        ids = [f"doc_{idx:03d}" for idx in range(len(documents))]

        # 批量生成 Embeddings
        embeddings = [self._get_embedding(doc) for doc in documents]

        # 存入向量数据库
        self.collection.add(
            documents=documents, embeddings=embeddings, metadatas=metadatas, ids=ids
        )
        print(f"✅ 知识库构建成功！当前索引条数: {self.collection.count()}")

    def query(self, user_query: str, top_k: int = 2) -> dict:
        """【在线检索与生成】端到端问答主逻辑"""
        # Step 1: Query 向量化
        query_embedding = self._get_embedding(user_query)

        # Step 2: 检索相似度最高的 Top-K 文本块
        search_results = self.collection.query(
            query_embeddings=[query_embedding], n_results=top_k
        )

        retrieved_docs = search_results["documents"][0]
        retrieved_metas = search_results["metadatas"][0]
        distances = search_results["distances"][0]

        # Step 3: 拼接 Context 上下文
        context_str = "\n\n".join(
            [
                f"[资料{i+1}] (来源: {retrieved_metas[i].get('source', '未知')}):\n{doc}"
                for i, (doc, meta) in enumerate(zip(retrieved_docs, retrieved_metas))
            ]
        )

        # Step 4: 组装 Prompt
        prompt = f"""系统指令：你是一个严谨的企业知识库 AI 助手。
请**严格仅根据**下方的 [参考上下文] 来回答用户的 [问题]。

约束条件：
1. 如果参考上下文中没有提到答案所需的关键信息，请直接回答：“根据已知知识库内容，无法回答该问题。”
2. 绝不能捏造、编造或根据通用常识补充任何知识库未提及的事实。
3. 你的回答应当简洁、客观。

[参考上下文]:
{context_str}

[用户问题]:
{user_query}
"""

        # Step 5: 调用 LLM 生成最终回答
        response = self.llm_client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,  # 设为 0 降低随机性，确保严格基于 Context
        )

        reply = response.choices[0].message.content

        return {
            "query": user_query,
            "reply": reply,
            "context_used": context_str,
            "raw_retrieved": list(zip(retrieved_docs, distances)),
        }


# =====================================================================
# 🧪 2. 测试数据集与 3 个典型场景验证
# =====================================================================
if __name__ == "__main__":
    # 清理旧的 DB 目录以保证全新测试
    if os.path.exists("./chroma_rag_db"):
        shutil.rmtree("./chroma_rag_db")

    # 1. 准备私有企业规范语料 (模拟真实场景)
    sample_docs = [
        "NexusTech 公司的员工年假制度规定：入职满 1 年的员工享有 10 天带薪年假，试用期员工（前 3 个月）不享有带薪年假。",
        "NexusTech 公司的出差餐补标准为：一线城市（北京、上海、深圳）每天 250 元，二线及其他城市每天 150 元。",
        "NexusTech 公司的远程办公政策：每周五允许员工申请居家办公（WFH），需提前 24 小时在 HR 系统报备。",
        "关于报销审批流程：金额低于 1000 元由直属部门经理审批，超过 1000 元需由部门 VP 与财务总监双重审批。",
    ]

    sample_metas = [
        {"source": "员工手册_HR_01.md"},
        {"source": "财务报销规范_FIN_02.md"},
        {"source": "员工手册_HR_01.md"},
        {"source": "财务报销规范_FIN_02.md"},
    ]

    # 2. 初始化 Pipeline 并装载知识库
    rag = BasicRAGPipeline()
    rag.build_knowledge_base(sample_docs, sample_metas)

    # 3. 准备 3 个具有代表性的测试问题
    test_questions = [
        "测试 1 (精准匹配): NexusTech 公司的员工试用期有带薪年假吗？年假几天？",
        "测试 2 (条件推理): 我在北京出差两天，餐补一共可以报销多少钱？",
        "测试 3 (拒答验证/超出知识库): NexusTech 公司加班有加班费吗？补贴标准是多少？",
    ]

    print("\n" + "=" * 70)
    print("🚀 开始运行 3 个关键测试，验证 RAG 回答质量与防幻觉效果")
    print("=" * 70 + "\n")

    for q in test_questions:
        print(f"❓ 【提问】: {q}")
        res = rag.query(q, top_k=2)
        print(f"💡 【AI 最终回答】:\n{res['reply']}\n")
        print(f"🔍 【检索到并使用的 Context】:\n{res['context_used']}")
        print("-" * 70 + "\n")
