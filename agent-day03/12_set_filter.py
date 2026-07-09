# 1. 定义系统合规黑名单（敏感词）
# 💡 前端心智：由于黑名单是固定的、不可变的，我们用集合存储，检索效率是 O(1)
SECURITY_BLACKLIST = {"rm -rf", "sudo", "drop database", "jailbreak"}

def clean_and_verify_tags(raw_llm_tags: list[str]) -> tuple[list[str], bool]:
    """
    清洗大模型吐出的标签列表
    1. 去除重复项
    2. 去除两端空格并统一转小写
    3. 检查是否命中黑名单
    """
    # 🌟 步骤 A：利用列表推导式清洗空格和大小写，并直接灌入 set 去重
    clean_set = {tag.strip().lower() for tag in raw_llm_tags}
    
    print(f"🧼 经集合去重及规范化后的标签: {clean_set}")
    
    # 🌟 步骤 B：利用集合的“交集运算 (&)”一枪判定是否安全
    # 如果交集不为空，说明命中了黑名单
    hit_blacklist = clean_set & SECURITY_BLACKLIST
    
    if hit_blacklist:
        print(f"🛑 安全警告！检测到非法越狱指令: {hit_blacklist}")
        return [], False
        
    # 将合规的数据转回 list 返回
    return list(clean_set), True

# --- 模拟连续测试 ---

# 测试案例 1：大模型吐出了一堆带有空格、重复的前端技术栈
llm_output_1 = ["React", " Next.js ", "react", "TypeScript", "Next.js"]
result_1, is_safe_1 = clean_and_verify_tags(llm_output_1)
print(f"👉 案例 1 最终安全输出: {result_1}\n" + "-"*50)

# 测试案例 2：大模型被用户恶意 prompt 越狱，带入了危险指令
llm_output_2 = ["React", "SUDO", "next.js", "rm -rf  "]
result_2, is_safe_2 = clean_and_verify_tags(llm_output_2)
print(f"👉 案例 2 最终安全输出: {result_2}")