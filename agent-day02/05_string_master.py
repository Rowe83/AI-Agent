# 模拟大模型不听话吐出的原始文本
raw_llm_output = """```json
{"model": "deepseek-v3", "tokens": 4096, "latency": 1.245}
```"""

print("1. 🚨 收到原始垃圾文本：")
print(raw_llm_output)
print("-" * 40)

# 2. 利用切片剥离前后的 ```json 和 ```
# 观察特征：头部有 7 个字符 (```json\n)，尾部有 4 个字符 (\n```)
clean_json = raw_llm_output[7:-4]

print("2. 🧼 经过切片处理后的干净数据：")
print(clean_json)
print("-" * 40)

# 3. 使用 F-string 高级特性进行前端样式的 Debug 输出
import json
data = json.loads(clean_json)

model = data["model"]
tokens = data["tokens"]
time_cost = data["latency"]

print("3. 📊 最终 F-string 格式化看板：")
# :.2f 格式化耗时，= 号直接打印变量状态
print(f"【模型核心指标】 -> {model.upper()}")
print(f"处理耗时: {time_cost:.2f} 秒")
print(f"性能对齐: {tokens=}")