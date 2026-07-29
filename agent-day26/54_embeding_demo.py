import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv
from openai import APITimeoutError, APIConnectionError, OpenAI
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer

# =====================================================================
# 🚀 1. 初始化客户端与文本数据集
# =====================================================================
# 从仓库根目录加载 .env（在 agent-day26/ 下直接运行也能读到）
ROOT_ENV = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ROOT_ENV)
load_dotenv()

# 嵌入接口必须用支持 embeddings 的 OpenAI 兼容服务。
# 注意：DeepSeek 目前只有 Chat，没有 /v1/embeddings，不能拿 OPENAI_API_KEY 去打 OpenAI。
api_key = os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL")
embedding_model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# 准备 3 组不同语义主题的测试文本
sentences = [
    # 科技/苹果
    "苹果公司发布了最新的 iPhone 智能手机",
    "库克宣布苹果在人工智能领域的最新进展",
    # 水果
    "今天在超市买了新鲜的红富士苹果",
    "香蕉和香橙都是非常富含维生素的水果",
    # 宇宙/物理
    "詹姆斯韦伯太空望远镜观测到了早期宇宙星系",
    "黑洞是宇宙中引力极强的极度密集天体",
]

labels = ["科技-1", "科技-2", "水果-1", "水果-2", "宇宙-1", "宇宙-2"]


def cosine_similarity(v1, v2):
    """计算两个向量的余弦相似度"""
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))


def fetch_openai_embeddings(texts: list[str]) -> np.ndarray | None:
    """调用 OpenAI 兼容 embeddings API；网络不通或未配置时返回 None。"""
    if not api_key:
        print("⚠️  未配置 DEEPSEEK_API_KEY，跳过云端嵌入接口。")
        return None

    print(f"正在调用嵌入 API ({base_url}, model={embedding_model}) ...")
    client = OpenAI(api_key=api_key, base_url=base_url, timeout=20.0)
    try:
        response = client.embeddings.create(model=embedding_model, input=texts)
    except (APITimeoutError, APIConnectionError) as exc:
        print(
            "⚠️  无法连接嵌入服务（ConnectTimeout / ConnectionError）。\n"
            f"   目标: {base_url}\n"
            "   常见原因：本机访问不了 api.openai.com，或未配置可用的 OPENAI_BASE_URL 代理/中转。\n"
            f"   原始错误: {exc}"
        )
        return None
    except Exception as exc:
        print(f"⚠️  嵌入 API 调用失败: {type(exc).__name__}: {exc}")
        return None

    return np.array([item.embedding for item in response.data])


def fetch_local_tfidf_embeddings(texts: list[str]) -> np.ndarray:
    """
    本地兜底：字符级 TF-IDF 向量。
    不依赖外网，足够演示「同类相近、异类疏远」与 PCA 可视化。
    """
    print("➡️  切换本地 TF-IDF 字符 n-gram 嵌入（无需外网）...")
    vectorizer = TfidfVectorizer(analyzer="char", ngram_range=(1, 2))
    return vectorizer.fit_transform(texts).toarray()


# =====================================================================
# 📡 2. 生成嵌入向量（云端优先，失败则本地兜底）
# =====================================================================
embeddings = fetch_openai_embeddings(sentences)
source = f"OpenAI-compatible ({embedding_model})"
if embeddings is None:
    embeddings = fetch_local_tfidf_embeddings(sentences)
    source = "local TF-IDF (char 1-2 gram)"

print(f"✅ 向量生成成功！来源: {source}，形状为: {embeddings.shape}")


# =====================================================================
# 🧮 3. 余弦相似度计算与对照
# =====================================================================
sim_tech1_tech2 = cosine_similarity(embeddings[0], embeddings[1])
sim_tech1_fruit1 = cosine_similarity(embeddings[0], embeddings[2])
sim_tech1_space1 = cosine_similarity(embeddings[0], embeddings[4])

print("\n--- 🔍 余弦相似度对决 ---")
print(f"同类科技 (iPhone vs 库克): {sim_tech1_tech2:.4f}")
print(f"跨类歧义 (iPhone vs 苹果水果): {sim_tech1_fruit1:.4f}")
print(f"完全异类 (iPhone vs 太空望远镜): {sim_tech1_space1:.4f}")

# =====================================================================
# 🎨 4. 高维向量降维与 3D 可视化 (PCA)
# =====================================================================
n_components = min(3, embeddings.shape[0], embeddings.shape[1])
print(f"\n正在将 {embeddings.shape[1]} 维空间通过 PCA 降维至 {n_components} 维并绘图...")

pca = PCA(n_components=n_components)
embeddings_3d = pca.fit_transform(embeddings)

fig = plt.figure(figsize=(10, 8))
if n_components == 3:
    ax = fig.add_subplot(111, projection="3d")
    colors = ["red", "red", "green", "green", "blue", "blue"]
    for i, (x, y, z) in enumerate(embeddings_3d):
        ax.scatter(x, y, z, color=colors[i], s=100, label=labels[i])
        ax.text(x + 0.01, y + 0.01, z + 0.01, labels[i], fontsize=10)
    ax.set_title(f"Embedding 3D Visualization ({source})", fontsize=14)
    ax.set_xlabel("X Axis")
    ax.set_ylabel("Y Axis")
    ax.set_zlabel("Z Axis")
else:
    ax = fig.add_subplot(111)
    colors = ["red", "red", "green", "green", "blue", "blue"]
    for i, point in enumerate(embeddings_3d):
        ax.scatter(point[0], point[1] if len(point) > 1 else 0, color=colors[i], s=100)
        ax.text(point[0], point[1] if len(point) > 1 else 0, labels[i], fontsize=10)
    ax.set_title(f"Embedding Visualization ({source})", fontsize=14)

plt.tight_layout()
# CI / 无显示环境用 Agg 时落盘；本机桌面环境直接弹窗
if os.environ.get("MPLBACKEND", "").lower() == "agg":
    out = Path(__file__).resolve().parent / "embedding_pca.png"
    plt.savefig(out, dpi=150)
    print(f"🖼️  已保存可视化图: {out}")
else:
    plt.show()
