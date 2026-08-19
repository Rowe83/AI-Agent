import os
import glob
import shutil
import fitz  # PyMuPDF 库，负责极速读取文本
import pdfplumber  # pdfplumber 库，负责精准提取表格
from typing import List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma

# =====================================================================
# 🛠️ 第一步：初始化大模型与 Embeddings 组件
# =====================================================================

# 1. 智谱 embedding-3 模型
zhipu_embeddings = OpenAIEmbeddings(
    model="embedding-3",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
    base_url=os.getenv("ZHIPU_BASE_URL"),
)

# 2. DeepSeek 对话模型
deepseek_llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    temperature=0.0,
)

# =====================================================================
# 📄 第二步：编写单页 PDF 解析核心函数
# =====================================================================


def parse_pdf_file(file_path: str) -> List[Document]:
    """
    输入: PDF 文件路径
    输出: 包含 Metadata (文件名、页码) 的 Document 对象列表
    """
    file_name = os.path.basename(file_path)
    page_documents = []

    # 同时打开两个解析器
    fitz_doc = fitz.open(file_path)  # 负责文本
    plumber_pdf = pdfplumber.open(file_path)  # 负责表格

    print(f"  📖 开始解析文件: {file_name}，共 {len(fitz_doc)} 页...")

    for page_idx in range(len(fitz_doc)):
        current_page_num = page_idx + 1
        fitz_page = fitz_doc[page_idx]
        plumber_page = plumber_pdf.pages[page_idx]

        # --- A. 提取正文文本 ---
        page_text = fitz_page.get_text().strip()

        # --- B. 提取表格（转为 Markdown）---
        table_md = ""
        raw_tables = plumber_page.extract_tables()
        if raw_tables:
            md_list = []
            for t in raw_tables:
                # 清理空单元格
                clean_t = [
                    [str(cell or "").replace("\n", " ").strip() for cell in row]
                    for row in t
                    if any(row)
                ]
                if len(clean_t) >= 2:
                    header = clean_t[0]
                    rows = clean_t[1:]
                    header_line = "| " + " | ".join(header) + " |"
                    sep_line = "| " + " | ".join(["---"] * len(header)) + " |"
                    body_lines = ["| " + " | ".join(r) + " |" for r in rows]
                    md_list.append(
                        header_line + "\n" + sep_line + "\n" + "\n".join(body_lines)
                    )
            table_md = "\n\n".join(md_list)

        # --- C. 扫描件检测与兜底 ---
        if len(page_text) < 10 and not table_md:
            # 如果既没有字，也没有表格，说明大概率是扫描件/图片页
            page_text = f"[注意：第 {current_page_num} 页文本过少，可能是扫描图像，建议开启 OCR 功能]"

        # --- D. 拼装页面最终文本 ---
        full_page_content = ""
        if page_text:
            full_page_content += f"【页面正文】:\n{page_text}\n"
        if table_md:
            full_page_content += f"\n【提取到的表格数据】:\n{table_md}\n"

        # --- E. 封装成带有详细 Metadata 的 Document ---
        if full_page_content.strip():
            doc = Document(
                page_content=full_page_content,
                metadata={
                    "source": file_name,  # 文件名
                    "page": current_page_num,  # 当前页码
                    "total_pages": len(fitz_doc),  # 总页数
                },
            )
            page_documents.append(doc)

    fitz_doc.close()
    plumber_pdf.close()
    return page_documents


# =====================================================================
# 🚀 第三步：多文件批量扫描、语义切片与向量入库 Pipeline
# =====================================================================


def process_and_ingest_pdf_folder(folder_path: str, persist_db_path: str):
    # 1. 扫描文件夹下的所有 PDF
    pdf_paths = glob.glob(os.path.join(folder_path, "*.pdf"))
    if not pdf_paths:
        print(f"❌ 在 {folder_path} 目录下没有找到任何 .pdf 文件！")
        return None

    print(f"🔍 扫描到 {len(pdf_paths)} 个 PDF 文件，准备处理...")

    # 2. 逐个解析 PDF 拿到按页划分的文档
    all_pages = []
    for path in pdf_paths:
        pages = parse_pdf_file(path)
        all_pages.extend(pages)

    print(f"\n✅ 提取完成，共收集到 {len(all_pages)} 个独立页面。")

    # 3. 使用中英文混合优化切分器进行 Chunk 切割
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=350,
        chunk_overlap=40,
        separators=["\n\n", "\n", "。", "！", "？", ". ", " ", ""],
    )
    chunks = splitter.split_documents(all_pages)
    print(f"✂️ 语义切分完成，共拆分为 {len(chunks)} 个小文本块 (Chunks)。")

    # 4. 调用智谱 embedding-3 入库 ChromaDB（有旧库先删再建，避免重复追加）
    if os.path.exists(persist_db_path):
        print(f"🗑️ 检测到旧库 {persist_db_path}，先删除再重建...")
        shutil.rmtree(persist_db_path)
    print("🚀 正在生成向量并存入 Chroma 数据库...")
    vectorstore = Chroma.from_documents(
        documents=chunks, embedding=zhipu_embeddings, persist_directory=persist_db_path
    )
    print("🎉 批量入库完毕！")
    return vectorstore


# =====================================================================
# 🧪 第四步：测试运行与答案验证
# =====================================================================

if __name__ == "__main__":
    TEST_FOLDER = "./my_pdf_docs"
    DB_PATH = "./zhipu_pdf_chroma"
    os.makedirs(TEST_FOLDER, exist_ok=True)

    # 1. 自动生成一份包含“正文 + 表格”的模拟 PDF 测试文件
    # Helvetica 不含中文，必须挂载 CJK 字体，否则中文会被写成 ·
    sample_pdf_path = os.path.join(TEST_FOLDER, "公司服务器采购指南_2026.pdf")
    cjk_font_candidates = [
        "/System/Library/Fonts/STHeiti Light.ttc",
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
        "/System/Library/Fonts/Supplemental/Songti.ttc",
        "/Library/Fonts/Arial Unicode.ttf",
    ]
    cjk_fontfile = next((p for p in cjk_font_candidates if os.path.exists(p)), None)
    if not cjk_fontfile:
        raise FileNotFoundError("未找到可用的中文字体，无法生成含中文的测试 PDF")

    doc = fitz.open()
    page = doc.new_page()
    page.insert_font(fontname="china", fontfile=cjk_fontfile)
    page.insert_text(
        (50, 50),
        "NexusTech 2026 年度服务器采购与运维指南\n"
        "采购流程：申请人需在 OA 系统提交申请，经部门主管与 IT 部门联合审批。\n"
        "标准质保政策：所有标准服务器均享有 3 年免费上门硬件质保。\n"
        "紧急响应标准：对于 P1 核心服务器故障，运维人员必须在 15 分钟内响应。\n",
        fontname="china",
    )
    doc.save(sample_pdf_path)
    doc.close()

    # 2. 执行批量解析与入库
    vectorstore = process_and_ingest_pdf_folder(TEST_FOLDER, DB_PATH)

    # 3. 执行一次检索问答验证
    if vectorstore:
        retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
        user_question = "请问 P1 核心服务器故障后，规定要在多长时间内响应？"

        print("\n" + "=" * 70)
        print(f"❓ 【用户提问】: {user_question}")
        print("=" * 70)

        # 检索相近的 Chunk
        matched_chunks = retriever.invoke(user_question)

        for i, chunk in enumerate(matched_chunks, start=1):
            print(f"\n📖 [检索匹配块 {i}]")
            print(
                f"  • 来源文件: {chunk.metadata['source']} (第 {chunk.metadata['page']} 页)"
            )
            print(f"  • 匹配到的文本:\n{chunk.page_content.strip()}")
