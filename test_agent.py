from agent import run_agent


question = input("请输入问题：")


answer = run_agent(question)


print("\n===== Agent回答 =====\n")

print(answer)