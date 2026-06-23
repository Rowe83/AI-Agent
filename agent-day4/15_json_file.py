import os
import json

DB_FILE = "agent_memory.json"

def save_memory(data: list | dict) -> None:
    """安全的保存函数"""
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            # 维持高标准序列化：2空格缩进，保护中文
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("💾 Agent 记忆已安全固化到硬盘。")
    except Exception as e:
        print(f"❌ 写入硬盘失败: {e}")

def load_memory() -> list | dict:
    """健壮的读取函数：完美处理文件不存在、文件损坏等极端边界"""
    # 🛡️ 边界 A：利用 os 模块检查文件是否存在，不存在直接初始化，绝不报 FileNotFound 错误
    if not os.path.exists(DB_FILE):
        print("ℹ️ 未检测到历史记忆文件，正在初始化干净的记忆库...")
        initial_data = [] # 默认给一个空列表（聊天历史常用）
        save_memory(initial_data)
        return initial_data

    # 🛡️ 边界 B：文件虽然存在，但可能被用户不小心改坏了（JSON 语法错误）
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # 如果文件损坏，提示用户，并优雅返回空数据，而不是硬性崩溃
        print(f"⚠️ 警告: 检测到本地文件 {DB_FILE} 已损坏！已自动启动安全隔离并返回空数据。")
        return []

# --- 模拟生产运行流水线 ---

# 1. 首次启动：尝试加载记忆（此时本地根本没有这个文件）
memory = load_memory()

# 2. 模拟 Agent 产生了新的对话记忆并存入
memory.append({"role": "user", "content": "帮我看看这个 villa 户型图"})
memory.append({"role": "assistant", "content": "收到，该低密度住宅进深极佳..."})

# 3. 将新记忆安全写入硬盘
save_memory(memory)

# 4. 二次读取：验证硬盘数据是否完美同步
print("\n🔄 重新加载系统，从硬盘读取到的记忆看板：")
fresh_memory = load_memory()
print(json.dumps(fresh_memory, indent=2, ensure_ascii=False))