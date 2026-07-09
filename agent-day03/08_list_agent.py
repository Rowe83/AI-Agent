def manage_context(history_list, new_message, max_turns=4):
    """
    SaaS 核心逻辑：安全追加新消息，并确保上下文不超过 max_turns 条。
    history_list: 当前历史对话列表
    new_message: 新进来的对话文本
    max_turns: 最大允许保留的单条消息数
    """
    # 1. 使用 append 追加新消息（改变原列表）
    history_list.append(new_message)
    print(f"📥 收到新消息，当前总数: {len(history_list)} 条")
    
    # 2. 使用切片进行滑动窗口裁剪
    # 如果超过最大限制，只保留最后 max_turns 条
    if len(history_list) > max_turns:
        print(f"⚠️ 触发阈值，正在切片裁剪历史...")
        history_list = history_list[-max_turns:]
        
    return history_list

# --- 模拟生产环境的连续对话 ---
context = []

# 第 1 轮对话
context = manage_context(context, "User: 你好")
context = manage_context(context, "AI: 你好！我是你的 Agent")

# 第 2 轮对话
context = manage_context(context, "User: 帮我写个前端组件")
context = manage_context(context, "AI: 没问题，这是代码...")

# 第 3 轮对话（此时总数达到 5 条，突破设定的 max_turns=4）
context = manage_context(context, "User: 谢谢，能帮我转成 Python 吗？")

print("\n📊 最终喂给大模型的安全上下文看板：")
print("=" * 40)
for msg in context:
    print(f"  {msg}")
print("=" * 40)