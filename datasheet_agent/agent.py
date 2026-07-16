# datasheet_agent/agent.py

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_siliconflow import ChatSiliconFlow

# 导入爬虫同学封装好的工具
from datasheet_tools import search_datasheet, download_datasheet

load_dotenv()

# ========== 1. 初始化 LLM（硅基流动 + 智谱模型） ==========
llm = ChatSiliconFlow(
    model=os.getenv("MODEL", "zai-org/GLM-5.2"),
    base_url=os.getenv("BASE_URL", "https://api.siliconflow.cn/v1"),
    api_key=os.getenv("API_KEY"),
    temperature=0.1
)

# ========== 2. 定义工具 ==========
@tool
def query_vector_db(question: str, chip_model: str = "") -> str:
    """从向量数据库中检索芯片数据手册相关内容。参数: question - 用户问题"""
    return f"正在检索 '{question}' 的相关内容...（等待向量数据库接入）"

# ========== 3. 构建 Agent ==========
agent = create_agent(
    model=llm,
    tools=[search_datasheet, download_datasheet, query_vector_db],
    system_prompt="""你是一位专业的硬件工程师，专门回答芯片数据手册相关问题。

工作流程：
1. 当用户询问某个芯片型号时，先调用 search_datasheet 搜索可用厂商
2. 根据搜索结果，调用 download_datasheet 下载对应数据手册
3. 下载完成后，再调用向量数据库查询具体参数（等数据库接入后）

规则：
- 严格基于 Datasheet 原文回答，严禁编造参数
- 回答时附上引用页码
- 回答语言与用户提问语言保持一致
"""
)

# ========== 4. 对外接口 ==========
def ask(question: str, thread_id: str = "default") -> str:
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]}
    )
    return result["messages"][-1].content

# ========== 5. 测试 ==========
if __name__ == "__main__":
    print("🤖 Agent 已就绪，已集成爬虫工具！")
    print(ask("帮我查找 LM337 的数据手册"))