# 模拟 Multi-Agent 团队对一份简历生成的各项多层级原始评分
cv_audit_scores = {
    "Code_Quality": 92,
    "Architecture_Design": 88,
    "Security_Compliance": 74,
    "Performance_Optimization": 62
}

print("1. 📊 正在导出需要紧急整改（分数低于 80）的核心技术维度：")
print("=" * 50)
# 练习 A：利用 .items() 同时遍历键值
for dimension, score in cv_audit_scores.items():
    if score < 80:
        print(f"❌ 警告 -> 维度: {dimension} | 当前得分: {score}分 (未达标)")
print("=" * 50)


print("\n2. 🚀 启动一键高光重构（筛选出优秀维度，并打上高亮标签）：")
# 练习 B：利用极其优雅的列表推导式，平替前端的 map + filter
# 需求：找出分数 >= 80 的维度，将其名字转为大写，并加上 [EXCELLENT] 前缀
highlight_reports = [f"[EXCELLENT] {dim.upper()}" for dim, score in cv_audit_scores.items() if score >= 80]

# 练习 C：遍历推导式生成的全新列表
for report in highlight_reports:
    print(f"  {report}")