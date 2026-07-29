import os
import re
import time
from pathlib import Path
from typing import List, Dict, Any
from pypdf import PdfReader


# =====================================================================
# 📦 1. 统一 Document 抽象与元数据提取器
# =====================================================================
class Document:
    def __init__(self, page_content: str, metadata: Dict[str, Any]):
        self.page_content = page_content
        self.metadata = metadata

    def __repr__(self):
        return f"<Document meta={self.metadata} content_len={len(self.page_content)}>"


class LocalDocumentLoader:
    """支持 PDF, TXT, MD 的通用本地文档加载器"""

    @staticmethod
    def load_file(file_path: str) -> List[Document]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        file_stat = path.stat()
        base_metadata = {
            "source": path.name,
            "file_path": str(path.resolve()),
            "file_size_bytes": file_stat.st_size,
            "created_time": time.strftime(
                "%Y-%m-%d %H:%M:%S", time.localtime(file_stat.st_mtime)
            ),
        }

        documents = []

        # 1. 解析 PDF 文件
        if path.suffix.lower() == ".pdf":
            reader = PdfReader(file_path)
            for page_idx, page in enumerate(reader.pages):
                text = page.extract_text() or ""
                page_meta = {
                    **base_metadata,
                    "page_number": page_idx + 1,
                    "total_pages": len(reader.pages),
                }
                documents.append(Document(page_content=text, metadata=page_meta))

        # 2. 解析 TXT / Markdown 文件
        elif path.suffix.lower() in [".txt", ".md"]:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            page_meta = {**base_metadata, "page_number": 1, "total_pages": 1}
            documents.append(Document(page_content=text, metadata=page_meta))

        return documents


# =====================================================================
# ✂️ 2. 递归字符切分器 (Recursive Character Splitter)
# =====================================================================
class RecursiveTextSplitter:
    def __init__(
        self,
        chunk_size: int = 300,
        chunk_overlap: int = 50,
        separators: List[str] = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # 分隔符优先级：段落 > 换行 > 句号/感叹号/问号 > 空间 > 逐字
        self.separators = separators or ["\n\n", "\n", "。", "！", "？", " ", ""]

    def split_documents(self, documents: List[Document]) -> List[Document]:
        final_chunks = []
        for doc in documents:
            raw_text = doc.page_content
            text_splits = self._split_text_recursively(raw_text, self.separators)

            # 合并微小片段，并应用 overlap 重叠窗口
            merged_texts = self._merge_splits(text_splits)

            for chunk_idx, chunk_text in enumerate(merged_texts):
                chunk_meta = {
                    **doc.metadata,
                    "chunk_id": f"{doc.metadata['source']}_p{doc.metadata.get('page_number',1)}_c{chunk_idx}",
                    "chunk_index": chunk_idx,
                    "chunk_size": len(chunk_text),
                }
                final_chunks.append(
                    Document(page_content=chunk_text, metadata=chunk_meta)
                )

        return final_chunks

    def _split_text_recursively(self, text: str, separators: List[str]) -> List[str]:
        final_splits = []
        separator = separators[-1]

        # 寻找当前能匹配上的最大优先级分隔符
        for idx, s in enumerate(separators):
            if s == "":
                separator = ""
                break
            if s in text:
                separator = s
                next_separators = separators[idx + 1 :]
                break

        # 按选定的分隔符切开
        splits = text.split(separator) if separator != "" else list(text)

        for s in splits:
            if len(s) < self.chunk_size:
                final_splits.append(s)
            else:
                # 依然超长，递归降级调用子分隔符切分
                if next_separators:
                    final_splits.extend(
                        self._split_text_recursively(s, next_separators)
                    )
                else:
                    final_splits.append(s)

        return final_splits

    def _merge_splits(self, splits: List[str]) -> List[str]:
        """合并微小文本块并处理 chunk_overlap 滑动窗口"""
        docs = []
        current_chunk = []
        current_len = 0

        for split in splits:
            split_len = len(split)
            if current_len + split_len > self.chunk_size:
                if current_chunk:
                    doc_text = "".join(current_chunk).strip()
                    if doc_text:
                        docs.append(doc_text)

                    # 保持 overlap: 保留尾部部分片段给下一个 chunk
                    while current_len > self.chunk_overlap and current_chunk:
                        popped = current_chunk.pop(0)
                        current_len -= len(popped)

            current_chunk.append(split)
            current_len += split_len

        if current_chunk:
            doc_text = "".join(current_chunk).strip()
            if doc_text:
                docs.append(doc_text)

        return docs


# =====================================================================
# 🚀 3. 测试运行
# =====================================================================
if __name__ == "__main__":
    # 创建模拟的 Markdown 案例文档
    sample_md = """# AI 架构师成长指南

## 第一章：大模型基础
大语言模型（LLM）是通过海量文本数据训练出来的深度学习模型。它能够理解自然语言并生成连续的文本。

## 第二章：RAG 架构实战
检索增强生成（RAG）结合了检索系统和生成模型的优势。其核心流程包括：文档加载、文本切分、嵌入向量化、向量索引以及上下文拼装生成。

通过合理的 chunk_size 与 chunk_overlap 设置，可以大幅提升检索的召回率，减少模型幻觉。建议生产环境中采用 300 到 500 字符的切分粒度。
"""
    test_file = "sample_guide.md"
    with open(test_file, "w", encoding="utf-8") as f:
        f.write(sample_md)

    print("📄 正在加载文档并提取元数据...")
    loader = LocalDocumentLoader()
    raw_docs = loader.load_file(test_file)
    print(f"✅ 加载成功！原始文档页数: {len(raw_docs)}")
    print(f"📌 页面元数据范例: {raw_docs[0].metadata}\n")

    print("✂️ 正在执行递归字符切分 (chunk_size=100, chunk_overlap=20)...")
    splitter = RecursiveTextSplitter(chunk_size=100, chunk_overlap=20)
    chunks = splitter.split_documents(raw_docs)

    print(f"✅ 切分完成！共生成 {len(chunks)} 个 Chunk。\n")
    print("--- 🔍 切分结果展示 ---")
    for idx, c in enumerate(chunks):
        print(
            f"【Chunk {idx}】[ID: {c.metadata['chunk_id']}] [Length: {c.metadata['chunk_size']}]"
        )
        print(f"内容: {c.page_content}")
        print("-" * 50)

    # 清理临时文件
    if os.path.exists(test_file):
        os.remove(test_file)
