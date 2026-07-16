import os
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
import glob
import shutil
from langchain_community.document_loaders import PyPDFLoader

from langchain_community.document_loaders import UnstructuredPDFLoader
# 1. 自动加载 .env 文件中的环境变量
load_dotenv()

# 2. 初始化硅基流动的 Embedding 模型
# 因为硅基流动兼容 OpenAI 格式，我们直接用 OpenAIEmbeddings 包装器
embeddings = OpenAIEmbeddings(
    model="BAAI/bge-m3",
    openai_api_key=os.getenv("EMBEDDING_API_KEY"), # 从环境文件中读取你的密钥
    openai_api_base="https://api.siliconflow.cn/v1"
)

print("正在从本地加载 PDF 数据手册...")

# 3. 动态读取下载目录下的所有 PDF (假设 PDF 放在上一层的 elecfans/downloads 目录下)
# 如果路径不对，请根据实际情况修改这个 pdf_dir
pdf_dir = "../elecfans/downloads"
pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))

if not pdf_files:
    print(f"❌ 未找到任何 PDF 文件，请确认路径 {pdf_dir} 是否正确！")
    exit()

all_docs = []
for file_path in pdf_files:
    print(f"正在进行OCR读取: {os.path.basename(file_path)}")


    loader = UnstructuredPDFLoader(
        file_path=file_path,
        mode="single",  # 将整篇文档合并，方便后续的 Recursive 分割
        strategy="hi_res",  # 开启高精度模式（自动调用 OCR 识别图片里的字）
        pdf_infer_table_structure=True  # 选填：尝试深度解析表格结构，对芯片手册很有帮助
    )
    docs = loader.load()

    file_name = os.path.basename(file_path)
    for doc in docs:
        doc.metadata["source_file"] = file_name

    all_docs.extend(docs)

print(f"共加载 {len(all_docs)} 页文档，正在进行文本切分...")

# 4. 文本切分（真实数据手册建议把块调大一点，避免切碎表格）
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    separators=["\n\n", "\n", "。", "，", " ", ""]
)
split_docs = text_splitter.split_documents(all_docs)
print(f"切分完毕，共生成 {len(split_docs)} 个检索块。")

persist_directory = "./chroma_db"#将数据库存在该文件夹

# 4.5 清理旧数据库，防止脏数据
if os.path.exists(persist_directory):
    print(f"检测到旧数据库目录 {persist_directory}，正在清空以防止数据重复...")
    shutil.rmtree(persist_directory)

print("正在调用 API 计算向量并存入新数据库...")

# 5. 存入 Chroma 数据库
vector_store = Chroma.from_documents(
    documents=split_docs,
    embedding=embeddings,
    persist_directory=persist_directory
)
print("向量数据库构建成功！")

# # 6. 测试检索（验证你的向量库是否能工作）
# query = "LM337 能用在什么场景？"
# # 寻找与问题最相关的 2 句话
# similar_docs = vector_store.similarity_search(query, k=2)

print("\n--- 检索测试结果 ---")
for i, doc in enumerate(similar_docs):
    print(f"匹配结果 {i+1}: {doc.page_content}")