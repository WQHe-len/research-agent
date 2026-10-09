import json

from llm import llm


def create_plan(question):

    prompt = f"""
你是一名专业的 AI 行业研究规划助手。

你的任务是：
根据用户提出的研究问题，将一个复杂的研究任务拆解成
3～5 个清晰、具体、可执行的研究子任务。

要求：

1. 每个子任务都应该围绕用户的核心问题。
2. 子任务之间尽量不要重复。
3. 子任务应该方便后续 Research Agent 分别执行。
4. 如果问题涉及行业研究，应优先考虑：
   - 市场规模与发展趋势
   - 核心技术
   - 竞争格局
   - 政策与产业环境
   - 机会与风险
5. 不要直接回答用户的问题。
6. 只负责制定研究计划。
7. 必须严格输出 JSON。
8. 不要输出 Markdown。
9. 不要输出 JSON 之外的任何文字。

输出格式：

{{
    "question": "{question}",
    "tasks": [
        {{
            "id": 1,
            "task": "具体研究任务",
            "purpose": "为什么需要研究这个问题"
        }},
        {{
            "id": 2,
            "task": "具体研究任务",
            "purpose": "为什么需要研究这个问题"
        }}
    ]
}}

用户研究问题：

{question}
"""

    response = llm.invoke(prompt)

    text = response.content.strip()

    try:
        plan = json.loads(text)

    except json.JSONDecodeError:

        print("Planner 输出不是合法 JSON：")
        print(text)

        return None

    return plan