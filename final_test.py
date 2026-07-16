# final_test.py
"""
智能体完整功能测试
测试：搜索、下载、向量检索、多轮对话记忆
"""

from datasheet_agent import ask
import time
import sys


def print_section(title):
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)


def test_search():
    """1. 测试搜索功能"""
    print_section("测试 1：搜索数据手册")
    question = "帮我查找 LM337 的数据手册"
    print(f"👤 用户: {question}")
    print("⏳ 处理中...")
    response = ask(question, thread_id="test_001")
    print(f"🤖 Agent:\n{response}")

    if "厂商" in response or "型号" in response:
        print("✅ 搜索功能通过")
    else:
        print("❌ 搜索功能异常")
    return response


def test_download():
    """2. 测试下载功能"""
    print_section("测试 2：下载数据手册")
    question = "请下载 STMICROELECTRONICS 的 LM337 数据手册"
    print(f"👤 用户: {question}")
    print("⏳ 处理中...")
    response = ask(question, thread_id="test_001")
    print(f"🤖 Agent:\n{response}")

    if "下载" in response and ("成功" in response or "保存" in response or "datasheets" in response):
        print("✅ 下载功能通过")
    else:
        print("⚠️ 请检查下载是否成功")
    return response


def test_vector_db():
    """3. 测试向量数据库检索"""
    print_section("测试 3：向量数据库检索")
    question = "LM337 的输出电压范围是多少？"
    print(f"👤 用户: {question}")
    print("⏳ 处理中...")
    response = ask(question, thread_id="test_001")
    print(f"🤖 Agent:\n{response}")

    # 检查是否包含参数信息
    keywords = ["V", "电压", "范围", "-1.2", "-37", "伏"]
    if any(k in response for k in keywords):
        print("✅ 向量数据库检索通过")
    else:
        print("⚠️ 未找到具体参数，请检查向量数据库是否已建好")
    return response


def test_memory():
    """4. 测试多轮对话记忆"""
    print_section("测试 4：多轮对话记忆")
    thread_id = "memory_test"

    # 第一轮：建立上下文
    q1 = "LM337 是什么芯片？"
    print(f"👤 用户（第1轮）: {q1}")
    r1 = ask(q1, thread_id=thread_id)
    print(f"🤖 Agent: {r1[:150]}...\n")
    time.sleep(0.5)

    # 第二轮：使用代词"它"测试记忆
    q2 = "它的输出电压范围是多少？"
    print(f"👤 用户（第2轮）: {q2}")
    r2 = ask(q2, thread_id=thread_id)
    print(f"🤖 Agent:\n{r2}")

    # 检查 Agent 是否理解了"它"指代 LM337
    if "LM337" in r2 or "电压" in r2:
        print("✅ 多轮对话记忆通过")
    else:
        print("⚠️ Agent 可能未记住上下文")
    return r2


def test_follow_up():
    """5. 测试连续追问"""
    print_section("测试 5：连续追问")
    thread_id = "followup_test"

    questions = [
        "LM337 的封装类型有哪些？",
        "它的最大输入电压是多少？",
        "典型应用电路是什么？"
    ]

    for i, q in enumerate(questions, 1):
        print(f"👤 用户（追问 {i}）: {q}")
        response = ask(q, thread_id=thread_id)
        print(f"🤖 Agent: {response[:200]}...\n")
        time.sleep(0.5)

    print("✅ 连续追问测试完成")


def run_all_tests():
    """运行所有测试"""
    print("🚀" * 30)
    print("   智能体功能完整测试")
    print("🚀" * 30)

    print("\n📌 前置检查：")
    print("1. 网络连接正常 ✓")
    print("2. API Key 已配置 ✓")
    print("3. Cookie 已配置 ✓")
    print("4. 向量数据库已建好（如未建好，测试3可能失败）")

    input("\n按 Enter 键开始测试...")

    try:
        test_search()
        time.sleep(1)

        test_download()
        time.sleep(1)

        test_vector_db()
        time.sleep(1)

        test_memory()
        time.sleep(1)

        test_follow_up()

        # 测试总结
        print_section("✅ 所有测试执行完毕！")
        print("📊 请检查以上输出，确认各功能是否正常")
        print("   - 如果测试1和2通过：搜索下载功能正常")
        print("   - 如果测试3通过：向量数据库功能正常")
        print("   - 如果测试4和5通过：多轮对话记忆功能正常")

    except KeyboardInterrupt:
        print("\n⏹️ 测试被中断")
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")


# ========== 主入口 ==========
if __name__ == "__main__":
    # 支持单独测试某个功能
    if len(sys.argv) > 1:
        test_name = sys.argv[1]
        if test_name == "search":
            test_search()
        elif test_name == "download":
            test_download()
        elif test_name == "vector":
            test_vector_db()
        elif test_name == "memory":
            test_memory()
        elif test_name == "followup":
            test_follow_up()
        else:
            print("可用测试: search, download, vector, memory, followup")
    else:
        run_all_tests()
        #测试2