from rag import search_knowledge
from llm import llm


def answer_question(question):

    # 1. 从知识库检索相关内容
    results = search_knowledge(question)

    # 2. 把检索结果整理成文本
    context = "\n\n".join(
        doc.page_content
        for doc in results
    )

    # 3. 构造Prompt
    prompt = f"""
你是一名专业的行业研究助手。

请根据下面提供的知识库资料回答用户的问题。

要求：
1. 优先使用知识库中的信息。
2. 不要编造知识库中不存在的事实。
3. 如果知识库没有相关信息，请明确告诉用户。
4. 回答要清晰、有条理。

===== 知识库资料 =====

{context}

===== 用户问题 =====

{question}

===== 回答 =====
"""

    # 4. 调用大模型
    response = llm.invoke(prompt)

    return response.content