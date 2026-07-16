import os
import sys
import time
import uuid
import re
from dotenv import load_dotenv

# 加载环境配置
load_dotenv()

# 导入Agent接口
from datasheet_agent import ask

# ========== 工具函数 ==========
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def clean_markdown(raw_text: str) -> str:
    """清除大模型返回的Markdown标记，优化终端显示"""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", raw_text)
    text = re.sub(r"^#{1,4}\s*", "", text, flags=re.MULTILINE)
    text = re.sub(r"`(.*?)`", r"\1", text)
    text = re.sub(r"\|", "  ", text)
    text = re.sub(r"-{3,}", "", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

def stream_print(text: str, delay: float = 0.02):
    """流式打字机输出"""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# ========== 主程序 ==========
def main():
    print("输入器件型号开始，或输入 /help 查看命令。\n")
    # 会话ID：保证同一会话的多轮记忆，/reset 时换新ID实现状态隔离
    thread_id = str(uuid.uuid4())

    while True:
        user_input = input(">: ").strip()
        if not user_input:
            continue

        # ===== 本地命令处理（不传给Agent） =====
        if user_input.lower() in ["/exit", "/quit", "q"]:
            print("\n程序已退出。")
            break
        if user_input == "/help":
            print("\n可用命令：")
            print("  /help   查看命令说明")
            print("  /clear  清空屏幕")
            print("  /reset  重置当前对话")
            print("  /exit   退出程序\n")
            continue
        if user_input == "/clear":
            clear_screen()
            continue
        if user_input == "/reset":
            thread_id = str(uuid.uuid4())
            print(" 对话已重置，请输入器件型号开始新的查询\n")
            continue

        # 调用Agent获取原始回答
        try:
            raw_answer = ask(question=user_input, thread_id=thread_id)
            # 清洗Markdown符号
            clean_ans = clean_markdown(raw_answer)
            # 加分隔线区分每一轮对话，观感更好
            split_line = "=" * 60
            stream_print(f"\n{split_line}")
            stream_print(clean_ans)
            stream_print(f"{split_line}\n")
        except Exception as e:
            print(f"❌ 请求失败：{str(e)}")

if __name__ == "__main__":
    main()