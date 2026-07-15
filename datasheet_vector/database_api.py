import os
import json
from dotenv import load_dotenv, find_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

# 自动寻找并加载 .env 文件
load_dotenv(find_dotenv())


def query_vector_db(question: str, chip_model: str) -> list[dict[str, str]]:
    """
    向量数据库检索接口，供 Agent 模块调用
    :param question: 用户的问题
    :param chip_model: 芯片型号
    :return: 包含 content, page, source 的字典列表
    """
    # 1. 初始化 Embedding 模型 (必须和你建库时一模一样)
    embeddings = OpenAIEmbeddings(
        model="BAAI/bge-m3",
        openai_api_key=os.getenv("EMBEDDING_API_KEY"),
        openai_api_base="https://api.siliconflow.cn/v1"
    )

    # 2. 定位到同目录下的 chroma_db 数据库文件夹
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "chroma_db"))

    vectorstore = Chroma(
        persist_directory=db_path,
        embedding_function=embeddings
    )

    # 3. 组合查询词并执行检索 (拼上芯片型号可以大幅提高准确率)
    search_query = f"{chip_model}的{question}"
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(search_query)

    # 4. 组装成 Agent 负责人要求的格式
    results = []
    for doc in docs:
        result_dict = {
            "content": doc.page_content,
            # PyPDFLoader 的页码是从 0 开始的，加 1 修正为真实页码
            "page": doc.metadata.get("page", 0) + 1,
            "source": doc.metadata.get("source_file", "未知文件")
        }
        results.append(result_dict)

    return results


# ==========================================
#测试区！直接运行本文件就会执行这里 ⬇
# ==========================================
if __name__ == "__main__":
    print("🚀 正在启动本地检索测试...\n")

    # 模拟 Agent 给你传了参数
    test_question = "What is the output voltage range?"
    test_chip = "LM337"

    print(f"🔍 模拟检索: 芯片=[{test_chip}], 问题=[{test_question}]\n")

    # 调用你自己的接口
    test_results = query_vector_db(question=test_question, chip_model=test_chip)

    # 漂亮地打印出返回的列表
    print("✅ 检索成功！返回给 Agent 的数据格式如下：")
    print(json.dumps(test_results, ensure_ascii=False, indent=2))