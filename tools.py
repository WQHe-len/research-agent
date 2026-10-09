from rag import search_knowledge


# 工具1：知识库搜索

def knowledge_search(query):

    results = search_knowledge(query)

    content = "\n\n".join(
        [
            doc.page_content
            for doc in results
        ]
    )

    return content



# 工具2：计算器

def calculator(expression):

    try:

        result = eval(expression)

        return str(result)

    except:

        return "计算失败"