# main.py
import json
# 🎯 完美对齐 ESM 体验：只从 functions 模块导入我们需要的业务函数
from functions import parse_github_commit, clean_and_verify_tags, audit_agent_gateway

print("🚀 [主程序] SaaS 后端运行总线启动...\n")

# --- 模拟业务数据 A：大模型吐出的脏数据 ---
llm_tags = [" Next.js 15 ", "next.js 15", "tailwind", "TypeScript "]
safe_tags = clean_and_verify_tags(llm_tags)
print(f"🎯 业务线 1 (标签清洗成功): {safe_tags}\n")


# --- 模拟业务数据 B：GitHub API 深度嵌套数据 ---
mock_github_payload = {
    "sha": "a5c7f89b2d1e4c3b6a8f9e0d7c5b3a1f4e2d6c8b",
    "commit": {
        "author": {"name": "  Alex_Frontend_Lead  "},
        "message": "fix: 优化导航栏切换效果，彻底解决首屏 Flicker 闪烁闪烁问题",
        "verification": {"verified": True}
    },
    "stats": {"total": 18, "additions": 15, "deletions": 3},
    "changed_files": [
        {"filename": "components/Navbar.tsx", "changes": 12},
        {"filename": "styles/global.css", "changes": 6}
    ]
}

# 调用重构后的核心解析器
audit_report = parse_github_commit(mock_github_payload)

# 运用 F-string 高级格式化打印精美业务看板
if audit_report:
    print("=" * 50)
    print("【GitHub 代码提交安全审计看板】")
    print("=" * 50)
    print(f"提交哈希值 : {audit_report['short_sha']}")
    print(f"代码贡献者 : {audit_report['author']}")
    print(f"提交信息流 : {audit_report['message']}")
    print(f"验证状态   : {audit_report['verification']}")
    print(f"变更统计   : +{audit_report['additions']} 行 / -{audit_report['deletions']} 行 (总计 {audit_report['total']} 行变更)")
    print("-" * 50)
    print("📦 变更文件明细：")
    
    # 遍历嵌套的文件列表 (for 循环遍历)
    for file in audit_report["files"]:
        print(f"  - [modified] {file['filename']} ({file['changes']} 处改动)")
    print("=" * 50 + "\n")


# --- 模拟业务数据 C：动态调度审计 ---
# 触发双星号字典解构传参
audit_agent_gateway("ResumeOptimizedAgent", model="deepseek-v3", temperature=0.0, tokens=4096)