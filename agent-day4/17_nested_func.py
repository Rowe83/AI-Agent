def walk_nested_data(data, level=0):
    """
    通用树状深度优先遍历器 (DFS)
    """
    indent = "  " * level # 根据当前深度自动增加缩进，形成完美的视觉树
    
    # 情况 A：如果当前节点是字典，遍历它的 key 和 value
    if isinstance(data, dict):
        for key, value in data.items():
            print(f"{indent}🔑 Key: {key}")
            # 递归探底
            walk_nested_data(value, level + 1)
            
    # 情况 B：如果当前节点是列表，遍历它的每个元素
    elif isinstance(data, list):
        for index, item in enumerate(data):
            print(f"{indent}🔢 [索引 {index}]")
            # 递归探底
            walk_nested_data(item, level + 1)
            
    # 情况 C：到了最底层的叶子节点（基础类型：str/int/bool等），直接打印值
    else:
        print(f"{indent}📄 Value: {data}")

# --- 测试这个硬核工具 ---
test_tree = {
    "SaaS_App": {
        "Tech_Stack": ["Next.js", "Tailwind", "Python"],
        "Active": True
    }
}

print("\n🌲 树状无限递归深度扫描展示：")
walk_nested_data(test_tree)