from agent_tool import run_tool_agent


while True:

    question=input(
        "\n请输入问题:"
    )


    answer=run_tool_agent(
        question
    )


    print(
        "\n=====回答====="
    )

    print(answer)