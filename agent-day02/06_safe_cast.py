def clean_and_parse_tokens(raw_input: str) -> int:
    """安全地将大模型返回的文本转换为合规的 Token 整数"""
    try:
        # 先去除两端可能存在的空格（相当于 JS 的 .trim()）
        clean_input = raw_input.strip()
        
        # 尝试转换
        return int(clean_input)
        
    except ValueError:
        # 💡 前端对照：如果转换失败（NaN），给一个生产环境的兜底默认值
        print(f"⚠️ 警告: 无法将 '{raw_input}' 转换为整数，已自动兜底为 0")
        return 0

# --- 测试我们的安全转换器 ---

# 情况 A：虽然带了空格和换行，但能安全清洗并转换
test_a = "  1024 \n"
tokens_a = clean_and_parse_tokens(test_a)
print(f"测试 A 结果: {tokens_a} (类型: {type(tokens_a)})\n")

# 情况 B：大模型抽风，返回了带字母的垃圾文本
test_b = "约 512 个"
tokens_b = clean_and_parse_tokens(test_b)
print(f"测试 B 结果: {tokens_b} (类型: {type(tokens_b)})\n")