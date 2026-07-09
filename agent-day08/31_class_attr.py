class FederatedAgent:
    """
    智能体联邦：利用【类属性】实施全局状态监控与熔断
    """
    # 🌟 类属性：全局断路器（False 代表正常，True 代表全线熔断）
    GLOBAL_BREAKER = False
    # 🌟 类属性：全联盟所有实例累加消耗的总 Token 计数器
    TOTAL_TOKEN_COUNTER = 0
    # 🌟 类属性：联盟硬性熔断阈值
    TOKEN_LIMIT = 5000

    def __init__(self, agent_name: str):
        # 实例属性：每个 Agent 独享
        self.agent_name = agent_name
        self.local_used_tokens = 0

    def execute_task(self, prompt_cost: int):
        """执行任务，并拉高全局计数器"""
        # 1. 检查全局断路器（通过类名安全访问）
        if FederatedAgent.GLOBAL_BREAKER:
            print(f"🛑 [{self.agent_name}] 拒绝执行：系统已触发全局熔断，拒绝任何外部请求。")
            return

        # 2. 模拟执行，累加局部和全局 Token
        self.local_used_tokens += prompt_cost
        FederatedAgent.TOTAL_TOKEN_COUNTER += prompt_cost  # 🌟 强行修改类属性内存
        
        print(f"🤖 [{self.agent_name}] 顺利执行任务。局部消耗: {self.local_used_tokens} | 🌍 联盟总计: {FederatedAgent.TOTAL_TOKEN_COUNTER}")

        # 3. 动态判定是否踩到全局雷区
        if FederatedAgent.TOTAL_TOKEN_COUNTER >= FederatedAgent.TOKEN_LIMIT:
            print(f"\n🚨 警告：联盟总消耗达到 {FederatedAgent.TOTAL_TOKEN_COUNTER}，已突破安全阈值！正在拉起全局断路器...")
            # 🌟 通过类名，一枪改掉全局类属性！
            FederatedAgent.GLOBAL_BREAKER = True


# --- 模拟多智能体并发流水线 ---

print("📡 初始化 Multi-Agent 生产总线...")
agent_1 = FederatedAgent("Billing_Agent")
agent_2 = FederatedAgent("Optimization_Agent")
agent_3 = FederatedAgent("Translation_Agent")

# 正常调度执行
agent_1.execute_task(2000)
agent_2.execute_task(2500)

# 此时总数达到了 4500，agent_3 继续跑任务，直接踩线触发熔断
agent_3.execute_task(1000)

print("-" * 50)
print("⚡️ 紧急追加任务尝试：")
# 此时任何实例再想执行，都会在网关被类属性的 GLOBAL_BREAKER 死死拦住
agent_1.execute_task(500)