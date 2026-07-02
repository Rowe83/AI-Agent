import logging
from pathlib import Path

# 1. 配置日志引擎
logging.basicConfig(
    level=logging.INFO, # 💡 控制门槛：低于 INFO 的日志（如 DEBUG）将被忽略
    format="%(asctime)s [%(levelname)s] %(filename)s:%(lineno)d - %(message)s",
    handlers=[
        logging.StreamHandler(),                     # 同时输出到终端控制台
        logging.FileHandler("agent.log", encoding="utf-8") # 同时追加写入到本地文件
    ]
)

# 2. 工业级调用示例
logging.debug("这是调测细节，线上看不见")
logging.info("🤖 智能体启动，正在连接远程网关...")
logging.warning("⚠️ 发现接口响应变慢，当前延迟: 1200ms")
logging.error("🛑 核心组件加载失败，尝试进行降级容灾！")