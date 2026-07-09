import json

# 1. 模拟大模型吐回来的不完美 JSON 文本
# 特征：带了 markdown 标记，且尾部有多余换行，但内部是标准的双引号
llm_raw_payload = """```json
{
    "model_name": "deepseek-chat",
    "usage": {
        "prompt_tokens": 1024,
        "completion_tokens": 256
    },
    "is_cached": true
}
```"""

def safe_parse_agent_response(raw_text: str) -> dict:
    """工业级安全反序列化器"""
    try:
        # 🌟 步骤 A：极简清洗（切片或替换，砍掉 markdown 标记）
        clean_text = raw_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text.replace("```json", "", 1)
        if clean_text.endswith("```"):
            clean_text = clean_text.rsplit("```", 1)[0]
        
        clean_text = clean_text.strip()
        
        # 🌟 步骤 B：反序列化 (String -> Dict)
        return json.loads(clean_text)
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 结构严重损坏，解析失败! 错误位置: {e}")
        # 返回一个合规的空字典，防止上层业务线 crash
        return {}

# --- 执行解析 ---
parsed_dict = safe_parse_agent_response(llm_raw_payload)

print("1. 🎯 成功反序列化为 Python 字典：")
print(f"数据类型: {type(parsed_dict)}")
print(f"直接取值 (模型名): {parsed_dict.get('model_name')}\n")

# --- 重新序列化输出（比如我们要把它作为 API 响应发给前端） ---
print("2. 📊 美化并支持中文的序列化输出 (dumps)：")

# indent=2 格式化为2空格缩进；ensure_ascii=False 保护中文不乱码
json_string_to_frontend = json.dumps(parsed_dict, indent=2, ensure_ascii=False)
print(json_string_to_frontend)