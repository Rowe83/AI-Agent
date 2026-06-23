import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

# 1. 加载环境变量
load_dotenv()

# 2. 初始化客户端 (100% 兼容 DeepSeek)
client = AsyncOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"  # 指向 DeepSeek 官方 API 端点
)

# 3. 异步流式调用函数 (使用内置类型提示)
async def stream_deepseek_response(prompt: str) -> None:
    try:
        # 开启 stream=True
        response = await client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个幽默、说话有梗的 AI 助手。"},
                {"role": "user", "content": prompt}
            ],
            stream=True  # 开启流式返回
        )
        
        print("🤖 DeepSeek 正在思考并逐字回复：\n" + "-"*40)
        
        # 💡 前端对照：这里的 async for 相当于 JavaScript 的 for await...of 循环
        # 用于消费可迭代的异步数据流 (ReadableStream)
        async for chunk in response:
            # 提取增量文本内容
            delta_content = chunk.choices[0].delta.content
            if delta_content:
                # print 默认会自动换行，使用 end="" 强行让它接在屁股后面打印
                # flush=True 强制让输入流立刻刷新到终端屏幕上
                print(delta_content, end="", flush=True)
                
        print("\n" + "-"*40 + "\n🚀 流式传输结束！")
        
    except Exception as e:
        print(f"\n❌ 发生调用错误: {str(e)}")

async def main():
    user_question = "请用 100 字以内，吐槽一下为什么程序员总是要配开发环境？"
    await stream_deepseek_response(user_question)

if __name__ == "__main__":
    # 显式启动异步事件循环
    asyncio.run(main())