import os
import glob
import fitz  # PyMuPDF
import pdfplumber
from typing import List
from dotenv import load_dotenv

load_dotenv()

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma

# =====================================================================
# 🛠️ 1. 初始化智谱 Embeddings 与 DeepSeek 模型
# =====================================================================
zhipu_embeddings = OpenAIEmbeddings(
    model="embedding-3",
    api_key=os.getenv("ZHIPUAI_API_KEY"),
    base_url=os.getenv("ZHIPU_BASE_URL"),
)

deepseek_llm = ChatOpenAI(
    model="deepseek-v4-flash",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("BASE_URL"),
    temperature=0.0,
)


# =====================================================================
# 📑 2. 核心函数：深度 PDF 提取器 (文字 + 表格转 Markdown + OCR探测)
# =====================================================================
def parse_single_pdf(pdf_path: str) -> List[Document]:
    """
    深度解析单份 PDF 文件：
    1. 优先提取表格并转化为 Markdown 字符串；
    2. 使用 PyMuPDF 提取正文；
    3. 检测扫描件并触发 OCR 兜底。
    """
    file_name = os.path.basename(pdf_path)
    extracted_docs = []

    # 1. 打开 pdfplumber 提取表格
    plumber_pdf = pdfplumber.open(pdf_path)

    # 2. 打开 PyMuPDF 提取纯文本
    fitz_doc = fitz.open(pdf_path)

    for page_num in range(len(fitz_doc)):
        page_text = ""
        fitz_page = fitz_doc[page_num]
        plumber_page = plumber_pdf.pages[page_num]

        # -------------------------------------------------------------
        # A. 提取表格并转化为 Markdown
        # -------------------------------------------------------------
        tables = plumber_page.extract_tables()
        table_markdown_list = []
        for table in tables:
            # 过滤包含空内容的行
            clean_table = [
                [str(cell or "").replace("\n", " ") for cell in row]
                for row in table
                if any(row)
            ]
            if len(clean_table) > 1:
                # 转换首行为表头，余下为内容
                header = clean_table[0]
                rows = clean_table[1:]
                md_table = (
                    f"| {' | '.join(header)} |\n| {' | '.join(['---']*len(header))} |\n"
                )
                for row in rows:
                    md_table += f"| {' | '.join(row)} |\n"
                table_markdown_list.append(md_table)

        # -------------------------------------------------------------
        # B. 提取原生页面纯文本
        # -------------------------------------------------------------
        raw_text = fitz_page.get_text().strip()

        # -------------------------------------------------------------
        # C. 扫描件/图片页检测与 OCR 兜底逻辑
        # -------------------------------------------------------------
        if len(raw_text) < 20 and len(table_markdown_list) == 0:
            # 文字极少，极大概率为扫描图片页
            print(
                f"  ⚠️ 警告: [{file_name}] 第 {page_num+1} 页疑似扫描件，触发 OCR 逻辑..."
            )
            try:
                import pytesseract
                from PIL import Image
                import io

                pix = fitz_page.get_pixmap(dpi=150)
                img = Image.open(io.BytesIO(pix.tobytes()))
                # 调用 pytesseract 处理中英文混合 OCR
                raw_text = pytesseract.image_to_string(img, lang="chi_sim+eng")
                raw_text = f"[OCR提取文本]:\n{raw_text}"
            except Exception as e:
                raw_text = f"[解析警告: 扫描件且 OCR 引擎不可用 - {str(e)}]"

        # -------------------------------------------------------------
        # D. 组装当前页面的完整文本内容
        # -------------------------------------------------------------
        combined_content = ""
        if raw_text:
            combined_content += f"正文内容:\n{raw_text}\n"
        if table_markdown_list:
            combined_content += "\n结构化表格数据:\n" + "\n".join(table_markdown_list)

        if combined_content.strip():
            # 创建带有丰富 Metadata 的 Document 对象
            doc = Document(
                page_content=combined_content,
                metadata={
                    "source": file_name,
                    "page": page_num + 1,
                    "total_pages": len(fitz_doc),
                },
            )
            extracted_docs.append(doc)

    plumber_pdf.close()
    fitz_doc.close()
    return extracted_docs


# =====================================================================
# 📂 3. 多 PDF 批量处理与向量化入库 Pipeline
# =====================================================================
def batch_process_pdfs(pdf_folder: str, db_dir: str):
    """
    扫描指定文件夹下的所有 PDF 并批量建立向量库
    """
    pdf_files = glob.glob(os.path.join(pdf_folder, "*.pdf"))
    if not pdf_files:
        print(f"❌ 目录下未找到任何 PDF 文件: {pdf_folder}")
        return None

    print(f"🔍 找到 {len(pdf_files)} 个 PDF 文件，开始深度解析...")
    all_page_docs = []

    for pdf_file in pdf_files:
        print(f"📄 正在解析: {os.path.basename(pdf_file)} ...")
        docs = parse_single_pdf(pdf_file)
        all_page_docs.extend(docs)

    print(f"\n✅ 提取完成！共得到 {len(all_page_docs)} 个页面文档。")

    # 4. 使用中英文优化切分器进行 Chunk 拆分
    cjk_text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=40,
        separators=["\n\n", "\n", "。", "！", "？", ". ", " ", ""],
    )

    split_chunks = cjk_text_splitter.split_documents(all_page_docs)
    print(f"✂️ 语义切分完成，共生成 {len(split_chunks)} 个文本 Chunk。")

    # 5. 写入向量数据库
    print("🚀 正在调用智谱 embedding-3 进行向量化并保存到 Chroma...")
    vectorstore = Chroma.from_documents(
        documents=split_chunks, embedding=zhipu_embeddings, persist_directory=db_dir
    )
    print("🎉 批量 PDF 入库成功！")
    return vectorstore


# =====================================================================
# 🧪 4. 模拟数据创建与运行测试
# =====================================================================
if __name__ == "__main__":
    # 创建测试 PDF 目录
    PDF_DIR = "./sample_pdfs"
    DB_DIR = "./pdf_chroma_db"
    os.makedirs(PDF_DIR, exist_ok=True)

    # 模拟创建一个简易 PDF 文件用于测试
    test_pdf_path = os.path.join(PDF_DIR, "2026_产品规格书.pdf")
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text(
        (50, 50),
        "NexusTech 产品规格说明书 (2026版)\n"
        "型号: NX-9000 Pro\n"
        "最大支持带宽: 100 Gbps\n"
        "工作温度范围: -20°C 至 75°C\n"
        "售后支持政策: 硬件质保期为 3 年，提供 7x24 小时技术服务支持。",
    )
    doc.save(test_pdf_path)
    doc.close()

    # 1. 批量处理入库
    vectorstore = batch_process_pdfs(PDF_DIR, DB_DIR)

    # 2. 执行查询验证
    if vectorstore:
        retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
        query = "NX-9000 Pro 的硬件质保期是几年？工作温度是多少？"

        print("\n" + "=" * 70)
        print(f"❓ 【提问】: {query}")
        print("=" * 70)

        retrieved_docs = retriever.invoke(query)
        for i, doc in enumerate(retrieved_docs, start=1):
            print(
                f"\n📖 [匹配 Chunk {i}] (出处: {doc.metadata['source']}, 第 {doc.metadata['page']} 页):"
            )
            print(doc.page_content)
