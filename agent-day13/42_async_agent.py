import asyncio
import aiohttp
import time

# 1. 定义单轨异步请求任务
async def run_single_agent_eval(session: aiohttp.ClientSession, agent_name: str, delay: float) -> dict:
    target_url = "https://httpbin.org/delay/1"  # 模拟一个强制延迟 1 秒的远程 API
    
    print(f"📡 [启动] {agent_name} 开始向云端发射异构请求...")
    
    try:
        # 发起真正的异步非阻塞 POST 请求
        payload = {"agent": agent_name, "task": "Code Review"}
        
        async with session.post(target_url, json=payload, timeout=5) as response:
            # 💡 避坑提示：读取响应体 json() 也必须写 await！它也是异步 I/O
            raw_res = await response.json()
            print(f"🟢 [回执] {agent_name} 请求成功归类！")
            return {"agent": agent_name, "status": "SUCCESS", "latency": delay}
            
    except Exception as e:
        print(f"🛑 [爆破] {agent_name} 遭遇连接超时或断路拦截: {e}")
        return {"agent": agent_name, "status": "FAILED", "error": str(e)}


# 2. 异步总控主阀门
async def main():
    agents = ["Router_Agent", "Coder_Agent", "Reviewer_Agent", "Security_Agent"]
    
    start_time = time.time()
    
    # 🌟 创建一个全应用共享的异步 HTTP 会话连接池
    async with aiohttp.ClientSession() as session:
        # 组装任务编队（生成 4 个处于等待状态的协程任务）
        tasks = [run_single_agent_eval(session, name, 1.0) for name in agents]
        
        print(f"🚀 正在通过 asyncio.gather 并发轰炸 {len(tasks)} 个 Agent 节点...")
        
        # 🌟 核心一枪：完美对齐 Promise.all()！
        # 4个请求同时发射，底层事件循环进行多轨交替调度
        results = await asyncio.gather(*tasks)
        
    end_time = time.time()
    
    print("\n=" * 50)
    print("📊 【并发调度收官审计快照】")
    print("=" * 50)
    for res in results:
        print(f"智能体: {res['agent']:<16} | 状态: {res['status']}")
    print("-" * 50)
    # 💡 见证奇迹：4个各自延迟 1 秒的任务，并发完工总耗时仅仅只有 1.x 秒，而不是 4 秒！
    print(f"⏱️ 异步总并发耗时: {end_time - start_time:.2f} 秒")
    print("=" * 50)


if __name__ == "__main__":
    # 激活全量事件循环引擎
    asyncio.run(main())