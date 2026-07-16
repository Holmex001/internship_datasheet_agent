import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import uuid
import re
import time
from dotenv import load_dotenv
from datasheet_agent import ask

# 加载环境变量
root_path = os.path.join(os.path.dirname(__file__), "..")
load_dotenv(os.path.join(root_path, ".env"))

# Markdown清洗
def clean_markdown(raw_text):
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", raw_text)
    text = re.sub(r"^#{1,6}\s", "", text, flags=re.MULTILINE)
    text = re.sub(r"`(.+?)`", r"\1", text)
    text = re.sub(r"\|", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

# 会话状态初始化
if "tid" not in st.session_state:
    st.session_state.tid = str(uuid.uuid4())
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("芯片Datasheet查询对话系统")

# 渲染历史对话
for user_msg, ai_msg in st.session_state.chat_history:
    with st.chat_message("user"):
        st.write(user_msg)
    with st.chat_message("assistant"):
        st.write(ai_msg)

# 输入框 + 加载提示 + 前端流式打字
user_input = st.chat_input("输入芯片型号，如LM337")
if user_input:
    # 用户消息
    with st.chat_message("user"):
        st.write(user_input)

    # 思考中加载提示
    with st.chat_message("assistant"):
        loading = st.empty()
        loading.write("🔍 正在检索芯片数据手册，请等待...")

    # 调用后端，阻塞等待完整返回
    full_response = ask(question=user_input, thread_id=st.session_state.tid)
    clean_text = clean_markdown(full_response)

    # 逐字符模拟流式输出
    with st.chat_message("assistant"):
        box = st.empty()
        show_str = ""
        for c in clean_text:
            show_str += c
            box.write(show_str)
            time.sleep(0.015)

    # 保存历史并刷新页面
    st.session_state.chat_history.append((user_input, full_response))
    st.rerun()

# 重置会话按钮（更换全新thread_id清空后端记忆）
if st.button("重置对话"):
    st.session_state.tid = str(uuid.uuid4())
    st.session_state.chat_history = []
    st.rerun()