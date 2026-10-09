import json

from llm import llm

from tools import (
    knowledge_search,
    calculator
)



TOOLS = {

    "knowledge_search": knowledge_search,

    "calculator": calculator

}



def run_tool_agent(question):


    # 第一步，让模型选择工具

    prompt = f"""

你是一个Agent。

你拥有以下工具：

1. knowledge_search
用途：
查询新能源汽车行业知识库


2. calculator
用途：
数学计算


如果需要工具，请严格返回JSON：

{{
"tool":"工具名称",
"input":"工具输入"
}}


如果不需要工具：

返回：

{{
"tool":"none"
}}



用户问题：

{question}

"""


    decision = llm.invoke(prompt)


    decision_text = decision.content.strip()


    print("\nAgent决策:")
    print(decision_text)



    # 尝试解析JSON

    try:

        action=json.loads(
            decision_text
        )


    except:

        return decision_text



    tool_name=action.get(
        "tool"
    )


    tool_input=action.get(
        "input"
    )



    # 不调用工具

    if tool_name=="none":

        return llm.invoke(
            question
        ).content



    # 调用工具

    if tool_name in TOOLS:


        result=TOOLS[tool_name](
            tool_input
        )


        final_prompt=f"""

你是一个AI助手。

用户问题：

{question}


工具返回结果：

{result}


请根据工具结果回答用户。

"""


        answer=llm.invoke(
            final_prompt
        )


        return answer.content



    return "没有找到对应工具"