import json

class SmartAgent:
    """
    工业级有状态智能体基类
    """
    def __init__(self, agent_name: str, model: str, temperature: float = 0.0):
        # 1. 在构造方法中初始化基本配置
        self.agent_name = agent_name
        self.model = model
        self.temperature = temperature
        
        # 2. 初始化智能体内存中的常驻状态（状态机历史）
        self.memory = []
        self.total_tokens_used = 0
        
    def add_chat_history(self, role: str, content: str):
        """往智能体记忆中追加一轮对话"""
        self.memory.append({"role": role, "content": content})
        
    def track_tokens(self, prompt_tokens: int, completion_tokens: int):
        """累加当前智能体消耗的 Token 总量"""
        subtotal = prompt_tokens + completion_tokens
        self.total_tokens_used += subtotal
        print(f"📈 [审计] {self.agent_name} 本轮消耗 {subtotal} Tokens，累计已消耗: {self.total_tokens_used}")

    def export_state_to_file(self):
        """将当前 Agent 的完整状态（快照）安全持久化到本地文件"""
        snapshot = {
            "agent_name": self.agent_name,
            "model": self.model,
            "total_tokens": self.total_tokens_used,
            "memory_snapshot": self.memory
        }
        
        filename = f"{self.agent_name.lower()}_state.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
        print(f"💾 状态锁死成功！当前 Agent 的全量快照已安全写入 {filename}")


# --- 模拟多智能体系统的实际运行 ---

print("🤖 正在实例化核心 Agent 节点...")
# 实例化（不需要写 new）
coder_node = SmartAgent("SaaS_Coder_Agent", model="deepseek-reasoner", temperature=0.2)

# 模拟第一轮思考与对话
coder_node.add_chat_history("user", "帮我用 Python 封装一个包含 __init__ 的 Class")
coder_node.add_chat_history("assistant", "没问题，这是为您写的高级类封装...")
coder_node.track_tokens(1024, 512)

# 模拟第二轮对话
coder_node.add_chat_history("user", "非常完美，请顺便加上持久化落盘方法")
coder_node.track_tokens(2048, 256)

# 将状态固化到硬盘
coder_node.export_state_to_file()