import json

agent_reply = {"status": "成功", "msg": "未发现敏感词"}

# ❌ 默认情况：会打印出 {"status": "\u6210\u529f", "msg": "\u672a\u53d1..."}
print(json.dumps(agent_reply))

# 🎯 正确姿势：完美输出原生中文
print(json.dumps(agent_reply, ensure_ascii=False))

# ❌ 这是一个用单引号包裹键值的 Python 字符串
bad_json_str = '{"model": "deepseek"}'

# json.loads(bad_json_str)  # ❌ 触发 json.decoder.JSONDecodeError 崩溃！
print(json.loads(bad_json_str))