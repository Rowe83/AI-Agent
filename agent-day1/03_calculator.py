def calc(a, b, op):
    if op == "add":
        return a + b
    elif op == "sub":
        return a - b
    elif op == "mul":
        return a * b
    elif op == "div":
        return a / b if b != 0 else "错误：除数不能为零"
    else:
        return "未知操作"
    
print("欢迎使用简单计算器！")
num1 = float(input("请输入第一个数字: "))
num2 = float(input("请输入第二个数字: "))
operation = input("请输入操作（add, sub, mul, div）: ")

result = calc(num1, num2, operation)
print(f"计算结果: {result}")

num = 90
is_even = True
CONNUM = 100
empty = None
num_list = ["1", "2", "3"]
print(num_list[0:2])
obj = {"name": "Alice", "age": 30}
print(obj["name"])
tem = f"打印变量 num 的值: {num}"
print(tem)