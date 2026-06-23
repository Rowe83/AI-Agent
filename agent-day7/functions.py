# functions.py
import json

def clean_and_verify_tags(raw_llm_tags: list[str]) -> list[str]:
    """Day 2: 集合去重与敏感词清洗"""
    SECURITY_BLACKLIST = {"rm -rf", "sudo", "drop database"}
    clean_set = {tag.strip().lower() for tag in raw_llm_tags}
    
    # 集合交集碰撞安全拦截
    if clean_set & SECURITY_BLACKLIST:
        print("🛑 [functions.py] 拦截危险越狱指令！")
        return []
    return list(clean_set)


def parse_github_commit(raw_data: dict) -> dict:
    """Day 2 期末测验：GitHub 嵌套 JSON 极限清洗器"""
    try:
        # 1. 切片截取前 7 位短哈希
        raw_sha = raw_data.get("sha", "")
        short_sha = raw_sha[:7]
        
        # 2. 深度嵌套抓取并规范化作者姓名
        raw_name = raw_data["commit"]["author"]["name"]
        clean_name = raw_name.strip().upper()
        
        # 3. 消息去重清洗
        raw_msg = raw_data["commit"]["message"]
        clean_msg = raw_msg.replace("闪烁闪烁", "")
        
        # 4. 状态条件判断映射 (if/else)
        is_verified = raw_data["commit"]["verification"]["verified"]
        status_icon = "✅ 已通过安全签名" if is_verified else "❌ 未签名"
        
        # 5. 提取变更统计
        stats = raw_data.get("stats", {})
        
        # 6. 提取文件明细列表
        files_list = raw_data.get("changed_files", [])
        
        # 将清洗完的数据打包成扁平字典返回
        return {
            "short_sha": short_sha,
            "author": clean_name,
            "message": clean_msg,
            "verification": status_icon,
            "additions": stats.get("additions", 0),
            "deletions": stats.get("deletions", 0),
            "total": stats.get("total", 0),
            "files": files_list
        }
    except KeyError as e:
        print(f"❌ [functions.py] 结构解析失败，缺少必要键名: {e}")
        return {}


def audit_agent_gateway(tool_name: str, *args, **kwargs):
    """Day 2: 运用 *args 和 **kwargs 的动态审计网关"""
    print(f"⚙️  [网关审计] 准备调用工具: {tool_name}")
    if args:
        print(f"   📥 匿名位置参数: {args}")
    if kwargs:
        print(f"   🎛️  命名配置参数: {kwargs}")


# 🌟 核心拦截守卫：本地测试沙箱
if __name__ == "__main__":
    print("\n🚨 [本地测试] 监测到 functions.py 正在被【直接独立运行】！启动沙箱自测...")
    
    # 自测 A：测试标签清洗
    dirty_tags = [" React ", "react", "sudo"]
    print(f"🧪 标签清洗自测: {clean_and_verify_tags(dirty_tags)}")
    
    print("-" * 40)
    print(f"ℹ️ 此时 functions.py 的 __name__ 真实值是: {__name__}\n")