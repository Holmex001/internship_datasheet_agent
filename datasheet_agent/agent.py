# datasheet_agent/agent.py

import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain.agents import create_agent
from langchain.tools import tool

# 加载 .env 环境变量
load_dotenv()

# ========== 1. 初始化 LLM ==========
llm = init_chat_model(
    model=os.getenv("MODEL", "deepseek-chat"),
    base_url=os.getenv("BASE_URL", "https://api.deepseek.com"),
    api_key=os.getenv("API_KEY"),
    temperature=0.1
)


# ========== 2. 定义工具（占位） ==========
@tool
def fetch_datasheet(chip_model: str) -> str:
    """搜索并下载指定型号芯片的数据手册。参数: chip_model - 芯片型号"""
    return f"正在搜索 {chip_model} 的数据手册...（等待爬虫模块接入）"


@tool
def query_vector_db(question: str, chip_model: str = "") -> str:
    """从向量数据库中检索芯片数据手册相关内容。参数: question - 用户问题"""
    return f"正在检索 '{question}' 的相关内容...（等待向量数据库接入）"


# ========== 3. 构建 Agent ==========
# 新版 LangChain 不需要 InMemorySaver，直接用 create_agent
agent = create_agent(
    model=llm,
    tools=[fetch_datasheet, query_vector_db],
    system_prompt="""你是一位专业的硬件工程师，专门回答芯片数据手册相关问题。

规则：
1. 优先从向量数据库检索到的内容回答
2. 如果用户问的手册还没下载，调用下载工具
3. 严格基于 Datasheet 原文回答，严禁编造参数
4. 回答时附上引用页码
5. 回答语言与用户提问语言保持一致
"""
)


# ========== 4. 对外接口（给 CLI 同学用） ==========
def ask(question: str, thread_id: str = "default") -> str:
    """
    处理用户问题，返回回答。

    参数:
        question: 用户输入的问题
        thread_id: 会话ID，用于多轮对话记忆

    返回:
        Agent 生成的回答文本
    """
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]}
    )
    return result["messages"][-1].content


# ========== 5. 测试 ==========
if __name__ == "__main__":
    print("🤖 Agent 已就绪！")
    print(ask("LM377 的输出电压范围是多少？"))