file_scores = [85, 92, 78, 96, 88]

map_list = list(map(lambda a: a + 5, file_scores))  # 每个分数加 5 分
print(map_list)

filter_res = list(filter(lambda a: a >= 80, file_scores))  # 过滤出大于等于 80 的分数
print(filter_res)

# 更推荐列表推导式： [a + 5 for a in file_scores] 或者 [a for a in file_scores if a >= 80]
print([a + 5 for a in file_scores])
print([a for a in file_scores if a >= 80])