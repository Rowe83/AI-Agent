# src/aggregator/main.py
import asyncio
import aiohttp
import time
import logging
from typing import Dict, Any
# 绝对路径导入
from src.aggregator.uitls import clean_and_flatten_data, export_to_audit_log

# 配置生产级日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] - %(message)s")


async def fetch_api_node(session: aiohttp.ClientSession, url: str, payload: Dict[str, Any], node_name: str) -> Dict[str, Any]:
    """单轨异步网络请求卫士"""
    logging.info(f"📡 [并发启动] 正在抓取 -> {node_name}")
    try:
        # 使用 async with 双层上下文锁死 application/json
        async with session.post(url, json=payload, timeout=5) as response:
            response.raise_for_status()
            data = await response.json()
            logging.info(f"🟢 [请求成功] -> {node_name} 报文已安全回执")
            return data
    except Exception as e:
        logging.error(f"❌ [网关爆破] -> {node_name} 遭遇灾难性失败: {e}")
        return {}


async def main() -> None:
    # 模拟三个上游异构接口发送的查询参数（我们使用 httpbin.org 作为网络沙箱）
    sandbox_url = "https://httpbin.org/post"
    
    weather_query = {"city": "  hangzhou  ", "temp": "28.5"}
    news_query = {
        "articles": [
            {"title": "AI SaaS 独立开发在 2026 年迎来全面爆发闪烁", "source": "TechCrunch"},
            {"title": "DeepSeek-R1 彻底改变了开源智能体的推理格局", "source": "Wired"}
        ]
    }
    exchange_query = {"pair": "USD_CNY", "rate": "7.285"}

    start_time = time.clock_gettime(time.CLOCK_MONOTONIC)

    # 1. 撑开全局异步连接池
    async with aiohttp.ClientSession() as session:
        # 2. 编排异步并发矩阵
        tasks = [
            fetch_api_node(session, sandbox_url, weather_query, "天气API_Node"),
            fetch_api_node(session, sandbox_url, news_query, "新闻API_Node"),
            fetch_api_node(session, sandbox_url, exchange_query, "汇率API_Node")
        ]
        
        # 3. 完美对齐 Promise.all()，三轨同发！
        raw_results = await asyncio.gather(*tasks)
        
    # 解构返回的异步矩阵
    weather_res, news_res, exchange_res = raw_results
    
    # 4. 进入数据洗涤流水线
    cleaned_rows = clean_and_flatten_data(weather_res, news_res, exchange_res)
    
    # 5. 持久化落盘
    export_to_audit_log(cleaned_rows)
    
    end_time = time.clock_gettime(time.CLOCK_MONOTONIC)
    
    print("\n" + "="*50)
    print(f"🎉 聚合引擎大获全胜！并发总耗时: {end_time - start_time:.2f} 秒")
    print("="*50 + "\n")


if __name__ == "__main__":
    # 火箭发射，拉起事件循环
    asyncio.run(main())