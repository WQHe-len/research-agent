from react_agent import react_agent


question=input(
    "请输入任务:"
)


answer=react_agent(
    question
)


print("\n=====最终答案=====\n")

print(answer)