def execute_task() -> tuple[int, str | None, float]:
    """
    模拟一个大模型工具调用的返回值
    返回一个固定三项的元组：(状态码, 错误描述, 耗时)
    """
    # 模拟命中错误：403 错误，原因无权限，耗时 0.45 秒
    return 403, "Permission Denied", 0.4523

# 1. 接收返回值并解构（体验多返回值）
status_code, error_msg, latency = execute_task()

# 2. 建立元组复合路由表 (把元组当成不可变的 Dict Key)
# 键为 (status_code, 是否有错误)
policy_matrix = {
    (200, False): "🚀 正常通过，流转至下一轮大模型思考",
    (403, True): "🛑 安全拦截：用户权限不足，触发 Human-in-the-loop 审批流",
    (500, True): "🔄 系统重试：大模型服务崩了，自动切换备用 DeepSeek 节点"
}

# 3. 提取判断路由（利用 bool(error_msg) 判断是否有错）
has_error = error_msg is not None
current_decision = policy_matrix.get((status_code, has_error), "❓ 未知状态，强制终止 Agent")

print("📊 Agent 路由监控看板")
print("=" * 45)
print(f"当前耗时: {latency:.2f} 秒")
print(f"决策结果: {current_decision}")
print("=" * 45)