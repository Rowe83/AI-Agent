import os
import shutil
import chromadb
from chromadb.utils import embedding_functions

# 定义数据落盘目录
DB_DIR = "./chroma_db_store"

# 如果重新运行，先清理历史磁盘数据（可选）
if os.path.exists(DB_DIR):
    shutil.rmtree(DB_DIR)

# =====================================================================
# 🚀 1. 初始化持久化客户端与配置 Embedding 函数
# =====================================================================
print("正在初始化 ChromaDB 持久化客户端...")
# PersistentClient 会自动将数据存入指定目录
client = chromadb.PersistentClient(path=DB_DIR)

# 使用 OpenAI 的 Embedding 模型（需要设置环境变量 OPENAI_API_KEY）
# 如果未设置，Chroma 默认会回退使用内置的 ONNX 版本的 all-MiniLM-L6-v2 模型
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small",
)

# 获取或创建 Collection（类比关系型数据库中的 Table）
# space 可选: "cosine" (余弦相似度), "l2" (欧氏距离), "ip" (内积)
collection = client.get_or_create_collection(
    name="tech_knowledge_base",
    embedding_function=openai_ef if os.getenv("OPENAI_API_KEY") else None,
    metadata={"hnsw:space": "cosine"},
)

print(f"✅ Collection '{collection.name}' 创建成功！")

# =====================================================================
# 📥 2. 添加文档 (Documents, Metadatas, IDs)
# =====================================================================
# 准备带有丰富元数据的 Chunk 数据
documents = [
    "苹果公司发布了搭载 M3 芯片的 MacBook Pro，性能提升明显。",
    "库克在最新的发布会上重点讲解了 Apple Intelligence 的隐私防护机制。",
    "红富士苹果是一种口感脆甜的水果，富含丰富的膳食纤维和维生素。",
    "DeepSeek 推出的 R1 模型在推理能力上取得了巨大的突破。",
    "Python 3.12 引入了更快的 GC 垃圾回收机制和优化的报错提示。",
]

metadatas = [
    {"category": "tech", "company": "Apple", "year": 2024, "type": "hardware"},
    {"category": "tech", "company": "Apple", "year": 2024, "type": "ai"},
    {"category": "fruit", "company": "None", "year": 2023, "type": "food"},
    {"category": "tech", "company": "DeepSeek", "year": 2025, "type": "ai"},
    {"category": "tech", "company": "Python", "year": 2023, "type": "language"},
]

ids = ["doc_001", "doc_002", "doc_003", "doc_004", "doc_005"]

print("\n正在向 ChromaDB 插入文档并生成向量...")
collection.add(documents=documents, metadatas=metadatas, ids=ids)
print(f"✅ 成功插入 {collection.count()} 条记录。")

# =====================================================================
# 🔍 3. 基础向量相似度查询 (Query)
# =====================================================================
query_text = "苹果的新手机或电脑硬件"
print(f"\n搜索查询: '{query_text}' (Top 2 最相似文档):")

results = collection.query(query_texts=[query_text], n_results=2)

for i in range(len(results["ids"][0])):
    doc_id = results["ids"][0][i]
    doc_text = results["documents"][0][i]
    meta = results["metadatas"][0][i]
    dist = results["distances"][0][i]
    print(f"  [{i+1}] ID: {doc_id} | 余弦距离: {dist:.4f}")
    print(f"      内容: {doc_text}")
    print(f"      元数据: {meta}\n")

# =====================================================================
# 🎯 4. 带元数据过滤（Metadata Filtering）的高级查询
# =====================================================================
print("--- 🔬 语法示范：高精度过滤查询 ---")
# 需求：查询与“人工智能”相关的技术，但仅限 2024 年及以后发布的 Apple 公司相关文档
filtered_query = "AI 深度学习"

filtered_results = collection.query(
    query_texts=[filtered_query],
    n_results=5,
    where={"$and": [{"company": {"$eq": "Apple"}}, {"year": {"$gte": 2024}}]},
)

print(f"查询关键词: '{filtered_query}' (条件: company == 'Apple' 且 year >= 2024)")
for i in range(len(filtered_results["ids"][0])):
    print(f"  -> 匹配到的文档: {filtered_results['documents'][0][i]}")
    print(f"     元数据: {filtered_results['metadatas'][0][i]}")

# =====================================================================
# 🔄 5. 持久化验证与重启加载测试
# =====================================================================
print("\n--- 🔄 测试断开与重启数据恢复 ---")
# 显式关闭客户端连接，模拟程序退出
del collection
del client

print("正在模拟重新启动应用程序并连接磁盘数据库...")
new_client = chromadb.PersistentClient(path=DB_DIR)

# 重新加载已经存在的 collection
reloaded_collection = new_client.get_collection(
    name="tech_knowledge_base",
    embedding_function=openai_ef if os.getenv("OPENAI_API_KEY") else None,
)

print(f"✅ 成功恢复数据库！当前集合数据量: {reloaded_collection.count()} 条。")
