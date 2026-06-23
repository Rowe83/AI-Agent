import os
import asyncio
from dotenv import load_dotenv
from openai import AsyncOpenAI

# 1. 加载 .env 文件中的环境变量
load_dotenv()

# 2. 初始化 DeepSeek 异步客户端
# DeepSeek 官方 SDK 推荐直接使用 openai 库进行兼容调用
client = AsyncOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"  # 指向 DeepSeek 官方 API 端点
)

# 3. 定义异步的 LLM 调用函数
async def ask_deepseek(prompt: str) -> str:
    try:
        # DeepSeek 同样支持标准的 Chat Completions 接口
        response = await client.chat.completions.create(
            model="deepseek-chat",  # 对应 DeepSeek-V3 模型；如果是推理模型则用 deepseek-reasoner
            messages=[
                {"role": "system", "content": "你是一个资深的 AI Agent 架构师，擅长用最硬核、最精准的技术语言回答问题。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1024
        )
        # 解析并返回模型生成的文本内容
        return response.choices[0].message.content
    except Exception as e:
        return f"DeepSeek 调用失败，错误信息: {str(e)}"

# 4. 主入口函数
async def main():
    print("🚀 正在向 DeepSeek 发起首次询问...")
    user_prompt = "请用一句话给有 7 年前端经验的工程师解释什么是 AI Agent。"
    
    result = await ask_deepseek(user_prompt)
    
    print("\n🤖 DeepSeek 回复：")
    print("-" * 50)
    print(result)
    print("-" * 50)

if __name__ == "__main__":
    # 启动 Python 异步事件循环
    asyncio.run(main())