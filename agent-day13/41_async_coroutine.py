import asyncio

# 1. 声明一个异步协程函数
async def fetch_ai_status():
    print("⏳ 开始请求大模型状态...")
    # ⚠️ 铁律：在异步世界里，绝对不能用传统的 time.sleep()，那会阻塞整个事件循环！
    # 必须用 asyncio 提供的异步非阻塞睡眠（对齐 JS 的 setTimeout Promise）
    await asyncio.sleep(1) 
    print("✅ 大模型健康度校验通过！")
    return "HEALTHY"

# 2. 启动核心入口
if __name__ == "__main__":
    # ❌ 直接调用 fetch_ai_status() 只会拿到一个孤零零的协程对象，啥都不会打印
    # 🎯 正确姿势：使用 asyncio.run() 作为火箭发射器，激活底层事件循环并运行协程
    result = asyncio.run(fetch_ai_status())
    print(f"最终结果: {result}")