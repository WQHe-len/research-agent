from rag import search_knowledge


query = "新能源汽车的电池技术有哪些发展方向？"

results = search_knowledge(query)


print("===== 检索结果 =====")

for i, doc in enumerate(results):

    print(f"\n--- 结果 {i + 1} ---")

    print(doc.page_content)