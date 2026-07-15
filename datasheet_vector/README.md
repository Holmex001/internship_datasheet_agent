#  数据手册向量知识库 (Datasheet Vector DB)

## 模块功能概述
本模块是主要实现了以下功能：
1. **文档解析**：读取elecfans\downloads下的 PDF 格式芯片数据手册，支持OCR深度解析复杂排版、电路图内嵌文字及表格。
2. **文本切分与向量化**：将长篇文档切分为合适的上下文块（Chunks），并通过调用云端大模型 API 进行高维向量化转换，能定位页码。
3. **本地化存储**：将向量数据持久化保存至本地 Chroma 数据库，支持防重写自动清理机制。
4. **检索接口提供**：封装了标准的 `query_vector_db` 函数，并返回包含原文、页码的结构化数据，供 Agent 大脑直接调用。

---

##  核心技术栈与模型
* **向量数据库**: `ChromaDB` 
* **Embedding 模型**: `BAAI/bge-m3`
* **底层 OCR 引擎**: `Tesseract`  + `Poppler`

---

## 各文件作用
chroma_db/ (本地数据库文件夹)

作用：ChromaDB 自动生成的索引文件。

注意：这个文件夹是代码自动生成的，里面全是计算机看懂的二进制和哈希数据。千万不要手动点开修改里面的任何东西。

build_vector_db.py (建库脚本)

作用：负责读取 PDF、做高级 OCR 扫描、切分段落、调用大模型生成向量，最后把数据存进 chroma_db 里。
爬虫抓了新的数据手册回来，跑这个脚本来更新数据库。

database_api.py (检索接口：给 Agent 用的“大门”)

## 环境依赖与安装指引 (⚠️ 重要)

本模块的依赖分为两部分，
请确保在使用 Conda 激活**虚拟环境**后安装

## 第一步：
```bash
#（必要）安装chroma
pip install chromadb langchain-chroma
```
## 第二步
若要支持OCR则进行以下安装
### tesseract
安装链接：https://digi.bib.uni-mannheim.de/tesseract/
安装时在other language里下载Math / Equation data

安装后把路径塞进环境变量。：

在 “系统变量” 列表中，打开path，把下载包含tesseract.exe的路径加进去。

在下方的 “系统变量” 处，点击 “新建”。
变量名 严格填写：TESSDATA_PREFIX
变量值 填写你安装目录下的 tessdata 路径，例如：C:\Program Files\Tesseract-OCR\tessdata

再次一路点击 “确定”后重启Pycharm
### poppler
```bash
# 安装 PDF 切图引擎(确保虚拟环境下执行）
conda install -c conda-forge poppler -y
```

## 第二步如果不想安装/多文件
在安装过requirements.txt后,将build_vector_db.py文件里第三部分替换成下面对应内容（OCR处理速度有限）
```bash
all_docs = []
for file_path in pdf_files:
    print(f"正在读取并解析: {file_path}")
    # 按照任务指导书要求，使用 layout 模式提取排版
    loader = PyPDFLoader(file_path, extraction_mode="layout")
    docs = loader.load()

    # 【细节优化】：把文件名存入 metadata，这样 Agent 就能区分这是哪家厂商的数据手册
    file_name = os.path.basename(file_path)
    for doc in docs:
        doc.metadata["source_file"] = file_name

    all_docs.extend(docs)
```