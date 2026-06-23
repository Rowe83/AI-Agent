# 模拟两个独立的 Agent 输出队列
agent_names = ["Router", "Coder", "Reviewer"]
agent_tokens = [1024, 4096, 512]

# 用 zip 把它们紧密咬合
zipped_iterator = zip(agent_names, agent_tokens)

# 转换成列表看看结构
print(list(zipped_iterator)) 
# 输出: [('Router', 1024), ('Coder', 4096), ('Reviewer', 512)]

for name, tokens in zip(agent_names, agent_tokens):
    print(f"Agent: {name}, Tokens: {tokens}")