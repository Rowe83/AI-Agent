class SmartAgent:
    # 类属性：全局全局全局计费费率
    rate = 0.002 

    def __init__(self, name):
        # 实例属性：每个 Agent 独有的名字
        self.name = name

# 实例化两个独立的 Agent
agent_a = SmartAgent("Router_Agent")
agent_b = SmartAgent("Coder_Agent")

# --- 1. 读取属性 ---
print(agent_a.name)  # -> "Router_Agent"
print(agent_b.name)  # -> "Coder_Agent" (实例属性，各自独立)

# 动态借道读取类属性
print(agent_a.rate)  # -> 0.002
print(agent_b.rate)  # -> 0.002 (它们指向类本身的同一块内存)

# --- 2. 致命盲区：通过【实例】去尝试修改类属性 ---
agent_a.rate = 0.005  
# ⚠️ 架构师注意：这行代码并没有修改类属性！
# 它实际上是给 agent_a 动态拦截并创建了一个【同名的实例属性】！
print(agent_a.rate)  # -> 0.005 (拿到了刚刚创建的实例属性)
print(agent_b.rate)  # -> 0.002 (类属性完好无损，agent_b 没受影响)

# --- 3. 正确姿势：通过【类本身】修改类属性 ---
SmartAgent.rate = 0.008  # 一枪爆头，修改全局源头

print(agent_a.rate)  # -> 0.005 (依然被它自己的局部同名实例属性拦截遮蔽)
print(agent_b.rate)  # -> 0.008 (看天棚！全局类属性被改，agent_b 瞬间同步！)