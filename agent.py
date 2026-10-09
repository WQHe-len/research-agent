from llm import llm
from rag import search_knowledge


def run_agent(question):

    # 第一步：让模型判断是否需要查询知识库

    decision_prompt = f"""
你是一个AI Agent。

你需要判断用户的问题是否需要查询新能源汽车行业知识库。

如果需要查询知识库，只回答：
SEARCH

如果不需要查询知识库，只回答：
DIRECT

用户问题：

{question}
"""

    decision = llm.invoke(decision_prompt)

    decision_text = decision.content.strip().upper()

    # 第二步：如果需要查询知识库
    if "SEARCH" in decision_text:

        results = search_knowledge(question)

        context = "\n\n".join(
            doc.page_content
            for doc in results
        )

        answer_prompt = f"""
你是一个专业的新能源汽车行业研究助手。

请根据下面的知识库资料回答问题。

不要编造知识库中没有的信息。

===== 知识库 =====

{context}

===== 用户问题 =====

{question}
"""

        answer = llm.invoke(answer_prompt)

        return answer.content

    # 第三步：不需要知识库，直接回答
    else:

        answer_prompt = f"""
你是一个AI助手。

请直接回答用户的问题。

用户问题：

{question}
"""

        answer = llm.invoke(answer_prompt)

        return answer.content