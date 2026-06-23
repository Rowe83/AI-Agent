# 模拟 GitHub API 返回的真实嵌套 JSON 树
raw_github_data = {
    "sha": "a5c7f89b2d1e4c3b6a8f9e0d7c5b3a1f4e2d6c8b",
    "commit": {
        "author": {
            "name": "Alex_Frontend_Lead",
            "email": "alex@company.com",
            "date": "2026-06-16T14:32:01Z"
        },
        "message": "fix: 优化导航栏切换效果，彻底解决首屏 Flicker 闪烁闪烁问题",
        "verification": {
            "verified": True,
            "reason": "valid"
        }
    },
    "stats": {
        "total": 18,
        "additions": 15,
        "deletions": 3
    },
    "changed_files": [
        {"filename": "components/Navbar.tsx", "status": "modified", "changes": 12},
        {"filename": "styles/global.css", "status": "modified", "changes": 6}
    ]
}

# ==================================================
# 【GitHub 代码提交安全审计看板】
# ==================================================
# 提交哈希值 : a5c7f89 (要求：利用切片只保留前 7 位短哈希)
# 代码贡献者 : ALEX_FRONTEND_LEAD (要求：去掉两端空格并强转大写)
# 提交信息流 : fix: 优化导航栏切换效果，彻底解决首屏 Flicker 问题
#            (要求：利用 replace() 剔除消息中重复的"闪烁闪烁"四个字)
# 验证状态   : ✅ 已通过安全签名 (要求：根据 verified 的布尔值，True 显示 ✅...，False 显示 ❌ 未签名)
# 变更统计   : +15 行 / -3 行 (总计 18 行变更)
# --------------------------------------------------
# 📦 变更文件明细：
#   - [modified] components/Navbar.tsx (12 处改动)
#   - [modified] styles/global.css (6 处改动)
# ==================================================

sha_str = raw_github_data.get("sha")[:7]
author_name = raw_github_data.get("commit", {}).get("author", {}).get("name", "").strip().upper()
commit_message = raw_github_data.get("commit", {}).get("message", "").replace("闪烁闪烁", "闪烁")
verification_status = raw_github_data.get("commit", {}).get("verification", {}).get("verified", False)
status_str = "✅ 已通过安全签名" if verification_status else "❌ 未签名"
additions = raw_github_data.get("stats", {}).get("additions", 0)
deletions = raw_github_data.get("stats", {}).get("deletions", 0)

print("=" * 50)
print("📊 GitHub 代码提交安全审计看板")
print("=" * 50)
print(f"提交哈希值 : {sha_str}")
print(f"代码贡献者 : {author_name}")
print(f"提交信息流 : {commit_message}")
print(f"验证状态   : {status_str}")
print(f"变更统计   : +{additions} 行 / -{deletions} 行 (总计 {additions + deletions} 行变更)")
print("-" * 50)
print("📦 变更文件明细：")

for files in raw_github_data.get("changed_files", []):
    filename = files.get("filename")
    status = files.get("status")
    changes = files.get("changes")
    print(f"  - [{status}] {filename} ({changes} 处改动)")
print("=" * 50)