# datasheet_agent/agent.py

import os
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_siliconflow import ChatSiliconFlow
from langgraph.checkpoint.memory import InMemorySaver  # ← 新增导入

# 导入爬虫同学封装好的工具
from datasheet_tools import search_datasheet, download_datasheet

# 导入向量数据库同学的检索函数
try:
    # from vector_db.database_api import query_vector_db as real_query_vector_db
    from datasheet_vector.database_api import query_vector_db as real_query_vector_db
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    print("⚠️ 警告: 未找到 vector_db 模块，向量数据库功能不可用")

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
    """
    从向量数据库中检索芯片数据手册的相关内容。

    参数:
        question: 用户的问题，如 "输出电压范围是多少？"
        chip_model: 芯片型号，如 "LM337"

    返回:
        检索到的文本内容，包含页码和来源
    """
    if not DB_AVAILABLE:
        return "⚠️ 向量数据库尚未接入，请等待数据库同学完成建库工作。"

    try:
        results = real_query_vector_db(question=question, chip_model=chip_model)

        if not results:
            return f"未在 {chip_model} 的数据手册中找到相关信息。"

        formatted_results = []
        for item in results:
            content = item.get("content", "")
            page = item.get("page", "未知")
            source = item.get("source", "未知文件")
            formatted_results.append(f"[页码: {page}] {content} (来源: {source})")

        return "\n\n".join(formatted_results)

    except Exception as e:
        return f"检索失败: {str(e)}"


# ========== 3. 构建 Agent（带记忆） ==========

# 3.1 创建短期记忆存储器
memory = InMemorySaver()  # ← 新增

# 3.2 创建 Agent 时传入 checkpointer
agent = create_agent(
    model=llm,
    tools=[search_datasheet, download_datasheet, query_vector_db],
    system_prompt="""你是一位专业的硬件工程师，专门回答芯片数据手册相关问题。

工作流程：
1. 当用户询问某个芯片型号时，先调用 search_datasheet 搜索可用厂商
2. 根据搜索结果，调用 download_datasheet 下载对应数据手册
3. 下载完成后，调用 query_vector_db 从向量数据库中检索具体参数
4. 基于检索结果回答用户的问题

规则：
- 优先从向量数据库检索到的内容回答
- 如果检索不到，再基于你的知识回答，但要说明"数据手册中未找到，以下为通用知识"
- 严格基于 Datasheet 原文回答，严禁编造参数
- 回答时附上引用页码
- 回答语言与用户提问语言保持一致
""",
    checkpointer=memory  # ← 新增：传入记忆存储器
)


# ========== 4. 对外接口 ==========
def ask(question: str, thread_id: str = "default") -> str:
    """
    处理用户问题，返回回答。支持多轮对话记忆。

    参数:
        question: 用户输入的问题
        thread_id: 会话ID，用于多轮对话记忆。相同 ID 的对话会保持上下文。

    返回:
        Agent 生成的回答文本
    """
    try:
        # 构建 config，传入 thread_id
        config = {"configurable": {"thread_id": thread_id}}  # ← 新增
        result = agent.invoke(
            {"messages": [{"role": "user", "content": question}]},
            config=config  # ← 新增：传入 config
        )
        return result["messages"][-1].content
    except Exception as e:
        return f"❌ Agent 处理出错: {str(e)}"


# ========== 5. 交互循环 ==========
def run_chat():
    """
    启动交互式对话循环，支持多轮对话
    """
    print("=" * 60)
    print("🤖 数据手册智能体已启动！")
    print("📌 请输入芯片型号或技术问题，如 'LM337 的输出电压范围是多少？'")
    print("📌 输入 'exit' 或 'quit' 退出对话")
    print("📌 输入 'clear' 清空对话记忆")
    print("=" * 60)

    session_id = "default"
    chat_count = 0

    while True:
        try:
            user_input = input("\n👤 你: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ["exit", "quit", "退出"]:
                print("👋 感谢使用，再见！")
                break

            if user_input.lower() in ["clear", "清空"]:
                chat_count += 1
                session_id = f"session_{chat_count}"
                print("✅ 对话记忆已清空")
                continue

            print("🤖 Agent: 思考中...", end="\r")

            answer = ask(user_input, thread_id=session_id)

            print(f"\n🤖 Agent: {answer}")

        except KeyboardInterrupt:
            print("\n👋 检测到中断，再见！")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")


# ========== 6. 测试入口 ==========
if __name__ == "__main__":
    run_chat()
    # print(ask("你好，请问你是谁？", thread_id="test1"))