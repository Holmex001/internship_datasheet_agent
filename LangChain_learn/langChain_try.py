from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.messages import SystemMessage
import os
from dotenv import load_dotenv
load_dotenv()

# LLM配置
BASE_URL = os.getenv("BASE_URL")
api_key = os.getenv("api_key")
MODEL =  os.getenv("MODEL")

PROMPT = "你是什么模型"

# 伪装代理
default_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# 1. 初始化 ChatOpenAI 模型
llm = ChatOpenAI(
    base_url=BASE_URL,
    api_key=api_key,
    model=MODEL,
    max_tokens=500,
    temperature=0.7,
    top_p=0.9,
    default_headers=default_headers  # 会直接传递给底层的 OpenAI 客户端
)

# 2. 构造消息

system_msg = SystemMessage(content="你是一名活泼的聊天助手，请用四川话回答问题")
user_msg = HumanMessage(content=PROMPT)

# [{"role": "user", "content": PROMPT}] 对应 LangChain 中的 HumanMessage
messages = [
    system_msg,
    user_msg
]
# 3. invoke调用模型
# response = llm.invoke(messages)

# # 4. 打印结果
# # 打印生成的文本内容
# print(response.content)
#
# # 打印完整的响应对象（包含 token 使用量、结束原因等元数据）
# print(response)


# 流式调用
count = 0
for chunk in llm.stream(messages):
    count += 1
    print(chunk.content, end="", flush=True)  # 逐Token实时输出
print(f"\n共收到 {count} 个 token")

