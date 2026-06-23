def invoke_llm(model, temperature, stream):
    print(f"正在向 {model} 发起请求，气温控制在 {temperature}，是否流式: {stream}")

# 生产环境：大模型配置通常死死存在一个字典里
current_config = {
    "model": "deepseek-reasoner",
    "temperature": 0.2,
    "stream": True
}

# ❌ 繁琐的传统写法：invoke_llm(current_config["model"], current_config["temperature"]...)
# 🎯 现代 Python 骚操作：用双星号直接解构字典传参！
invoke_llm(**current_config)  # 完美一枪命中！