import os
import sys
from dotenv import load_dotenv
from openai import OpenAI

# 1. 确保成功初始化环境
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("BASE_URL", "https://api.deepseek.com/v1")

if not api_key:
    print("🛑 错误：未在 .env 中检测到有效的 API Key！")
    sys.exit(1)

client = OpenAI(api_key=api_key, base_url=base_url)


def run_infinite_stream_chat():
    # 🌟 状态机核心：动态维护的多轮对话上下文内存
    # 置顶 system 人设，严格限制输出格式
    context_messages = [
        {
            "role": "system",
            "content": "你是一个极简主义的命令行 AI 助手。不废话，不客套，直奔技术核心，回答字数严格控制在 80 字以内。",
        }
    ]

    print("🤖 [AI 终端总线已接通] 输入 'exit' 或 'quit' 退出聊天室。\n")

    while True:
        # 👤 1. 捕获用户命令行输入
        user_input = input("\n👤 工程师 > ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit"]:
            print("👋 状态机正常销毁，下班！")
            break

        # 🌟 2. 将用户的问题追加进雪球状态机
        context_messages.append({"role": "user", "content": user_input})

        print("🤖 AI 思考中 > ", end="", flush=True)

        try:
            # 🌟 3. 发射流式请求 (stream=True)
            response_stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=context_messages,
                temperature=0.0,  # 锁死生产级精准度
                max_tokens=200,  # 强制熔断长度
                stream=True,  # 开启异步 SSE 传输模式
            )

            # 🌟 4. 徒手承接流式打字机碎片
            # 此时 response_stream 是一个生成器迭代器，每来一个词，循环就推进一次
            assistant_full_reply = ""

            for chunk in response_stream:
                # 逐层安全解构：choices -> [0] -> delta -> content
                delta_content = chunk.choices[0].delta.content

                if delta_content:  # 判空，部分结束帧（finish_reason）的 content 是 None
                    # end="" 确保不换行，flush=True 让控制台立刻吐字，不要在内存缓存区排队
                    print(delta_content, end="", flush=True)
                    assistant_full_reply += delta_content

            # 留出空行换行
            print()

            # 🌟 5. 极其重要：把大模型刚刚吐完的完整回答，追加进上下文，锁闭状态机闭环
            context_messages.append(
                {"role": "assistant", "content": assistant_full_reply}
            )

        except Exception as e:
            print(f"\n🛑 [通信中继爆破] 流式管道中断: {e}")
            # 如果失败了，把刚塞进去的 user 问题弹出，防止上下文队列污染
            context_messages.pop()


if __name__ == "__main__":
    run_infinite_stream_chat()
