from planner import create_plan


question = input("请输入研究问题：")

plan = create_plan(question)

print("\n===== Planner Result =====")

print(plan)