from react_agent import research_task


question = "2026年新能源汽车发展趋势是什么"

task = """
研究2026年新能源汽车市场规模、销量预测、
新能源汽车渗透率以及全球和中国市场增长趋势。
"""


result = research_task(
    question=question,
    task=task
)


print("\n")
print("========================================")
print("Research Task Result")
print("========================================")

print("\n【研究任务】")
print(result["task"])

print("\n【研究过程】")
print(result["history"])

print("\n【来源】")
for source in result["sources"]:
    print(source)