from rag_qa import answer_question


question = "新能源汽车行业2026年的具体销量是多少？"


answer = answer_question(question)


print("\n===== AI回答 =====\n")

print(answer)