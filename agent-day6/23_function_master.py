# 1. 定义一个通用的日志装饰流函数
def audit_tool_call(tool_name, *args, **kwargs):
    """动态审计任何工具的调用参数"""
    print(f"\n⚙️  [网关审计] 准备调用工具: {tool_name}")
    
    if args:
        print(f"   📥 收到匿名位置参数(元组): {args}")
    if kwargs:
        print(f"   🎛️  收到命名配置参数(字典): {kwargs}")

# 2. 定义两个具体的智能体工具
def calculate_cost(prompt_tokens, completion_tokens, rate=0.002):
    audit_tool_call("计费工具", prompt_tokens, completion_tokens, rate=rate)
    # 计算公式：总 token * 费率 / 1000
    total_cost = (prompt_tokens + completion_tokens) * rate / 1000
    return f"${total_cost:.4f}"

def format_resume_report(user_id, status="SUCCESS", **metadata):
    audit_tool_call("报表工具", user_id, status=status, **metadata)
    return f"📋 用户 {user_id} 的重构报告已生成。状态: {status} | 附加信息数: {len(metadata)}"


# --- 模拟 Agent 动态调度 ---

# 🎯 场景 A：调度计费工具（传入 2 个位置参数，1 个关键字参数）
cost_result = calculate_cost(1048, 256, rate=0.004)
print(f"🎯 计费执行结果: {cost_result}")

print("-" * 50)

# 🎯 场景 B：调度报表工具（传入 1 个位置参数，后面全是动态扩展的自定义元数据）
# 💡 前端心智：这完美解决了低代码或动态表单中，后端字段无限扩展的兼容问题
report_result = format_resume_report(
    "alex_lead_77", 
    status="SUCCESS", 
    completed_at="2026-06-21", 
    flicker_fixed=True,
    version=15
)
print(f"🎯 报表执行结果: {report_result}")