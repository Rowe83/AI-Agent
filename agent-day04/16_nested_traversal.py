# 模拟一份多智能体评审生成的嵌套报告数据
report_data = {
    "project_id": "saas_cv_007",
    "review_round": 2,
    "agents_feedback": [
        {
            "agent_name": "Frontend_Expert_Agent",
            "suggestions": [
                {"module": "首屏渲染", "score": 92, "fix": "增加 Next.js 15 的 PPR 预渲染"},
                {"module": "动画过渡", "score": 78, "fix": "修复全局导航栏切换时的闪烁问题"}
            ]
        },
        {
            "agent_name": "Security_Agent",
            "suggestions": [
                {"module": "鉴权拦截", "score": 98, "fix": "对 SSR 路由增加 JWT 边缘校验"}
            ]
        }
    ]
}

print("📊 开始解析深度嵌套的 Agent 报告数据...\n" + "="*50)

# 🌟 核心拆解步骤：
# 1. 第一层：feedback_list 是一个列表
feedback_list = report_data.get("agents_feedback", [])

# 2. 遍历列表，拿到里面的每一个字典
for agent_item in feedback_list:
    # 提取当前智能体的名称
    name = agent_item.get("agent_name")
    print(f"🤖 智能体模块: 【{name}】")
    
    # 3. 第二层嵌套：suggestions 又是当前字典里的一个列表
    suggestion_list = agent_item.get("suggestions", [])
    
    # 4. 继续遍历这个内部列表，拿到最底层的字典数据
    for s in suggestion_list:
        module_name = s.get("module")
        score = s.get("score")
        fix_action = s.get("fix")
        
        # 针对分数低的项目做重点标记
        alert_flag = "⚠️ 需紧急优化 ->" if score < 85 else "✅"
        
        # 优雅格式化输出
        print(f"  {alert_flag} 模块: {module_name} | 得分: {score}分")
        print(f"    具体对策: {fix_action}")
        
    print("-" * 50)