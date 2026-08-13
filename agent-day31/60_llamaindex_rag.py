import os
from dotenv import load_dotenv

# 1. 加载环境变量
load_dotenv()

from llama_index.core import Document, VectorStoreIndex, Settings, PromptTemplate
from llama_index.llms.openai_like import OpenAILike
from llama_index.embeddings.openai import OpenAIEmbedding

# =====================================================================
# 🛠️ 1. 初始化智谱 Embeddings 与 DeepSeek LLM (挂载至全局 Settings)
# =====================================================================
# LlamaIndex OpenAIEmbedding 的 model 参数只接受官方枚举
# (text-embedding-ada-002 / text-embedding-3-*)；智谱等兼容模型需用 model_name 绕过校验
# 1.1 智谱 embedding-3 模型 (使用 OpenAI 兼容类)
zhipu_embed_model = OpenAIEmbedding(
    model_name="embedding-3",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
    api_base=os.getenv("ZHIPU_BASE_URL"),
)

# 1.2 DeepSeek-v4-flash 模型 (使用 OpenAI 兼容类)
deepseek_llm = OpenAILike(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    api_base=os.getenv("BASE_URL"),
    temperature=0.0,
    is_chat_model=True,
    context_window=128000
)

# 1.3 配置全局默认设置
Settings.llm = deepseek_llm
Settings.embed_model = zhipu_embed_model
# 全局设置节点切块大小为 512 字符，重叠 50 字符
Settings.chunk_size = 512
Settings.chunk_overlap = 50

# =====================================================================
# 📦 2. 构造数据 (Document) 并创建 VectorStoreIndex
# =====================================================================

# 准备带有 Metadata 的文档对象
raw_documents = [
    Document(
        text="NexusTech 公司规定：员工入职满 1 年享有 10 天带薪年假，试用期员工（前 3 个月）无带薪年假。",
        extra_info={"source": "员工手册_HR_v2.pdf", "page": 12},
    ),
    Document(
        text="NexusTech 公司的出差餐补标准为：一线城市（北京、上海、深圳）每天 250 元，二线城市每天 150 元。",
        extra_info={"source": "财务报销规范_FIN_2026.pdf", "page": 5},
    ),
    Document(
        text="每周五为公司 WFH（远程办公）开放日，员工需提前 24 小时在 OA 系统中提交申请并获得主管批准。",
        extra_info={"source": "员工手册_HR_v2.pdf", "page": 18},
    ),
]

print("🚀 正在构建 LlamaIndex VectorStoreIndex 向量索引...")
# 一键完成：文本切块(Node) -> 向量化 -> 构建向量索引
index = VectorStoreIndex.from_documents(raw_documents)

# =====================================================================
# 📝 3. 定制带出处引用的 Prompt 模板与 Query Engine 响应
# =====================================================================

# LlamaIndex 的标准 Prompt 占位符为 {context_str} 与 {query_str}
qa_prompt_tmpl_str = (
    "你是一个严谨的企业知识库助手。\n"
    "请严格依据下方提供的 [参考文档] 回答用户的 [问题]。\n\n"
    "【参考文档】:\n"
    "{context_str}\n\n"
    "【问题】: {query_str}\n\n"
    "【回答规则】:\n"
    "1. 请在回答的关键句末尾标注出处来源。\n"
    "2. 若文档未提及，请明确回答'无法根据已知文档提供答案'。\n"
)
qa_prompt_tmpl = PromptTemplate(qa_prompt_tmpl_str)

# 构造开箱即用的 Query Engine
query_engine = index.as_query_engine(
    similarity_top_k=2,  # 检索 Similarity Top-2 Node
    text_qa_template=qa_prompt_tmpl,  # 注入定制的 QA Prompt
)

# =====================================================================
# 🧪 4. 运行查询与结果解析
# =====================================================================
if __name__ == "__main__":
    test_query = "请问我在深圳出差 3 天，餐补标准是多少？试用期可以请年假吗？"

    print("\n" + "=" * 70)
    print(f"❓ 【提问】: {test_query}")
    print("=" * 70 + "\n")

    # 执行查询
    response = query_engine.query(test_query)

    print(f"完整响应response: {response}\n")

    print(f"💡 【LlamaIndex + DeepSeek 回答】:\n{response.response}\n")

    print("📚 【LlamaIndex 检索到的 Node 元数据与出处追踪】:")
    for i, node_with_score in enumerate(response.source_nodes, start=1):
        node = node_with_score.node
        score = node_with_score.score
        source_file = node.metadata.get("source", "未知")
        page_num = node.metadata.get("page", "未知")

        print(f"  • [Node {i}] 相似度得分: {score:.4f}")
        print(f"    来源文件: {source_file} (第 {page_num} 页)")
        print(f"    文本切片: {node.get_content()}")
        print("-" * 50)
