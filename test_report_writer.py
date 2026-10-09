from report_writer import generate_report


question = "2026年新能源汽车行业发展趋势是什么？"


research_content = """
本地知识库：

新能源汽车行业的发展趋势主要包括电动化、智能化和网联化。

电池技术方向包括高能量密度电池、快充技术和固态电池。

智能驾驶包括环境感知、传感器融合、计算平台和自动驾驶算法。

智能座舱包括语音交互、车载大模型和多媒体系统。


网络搜索：

2026年新能源汽车行业市场化增长趋势明显，
固态电池产业化速度加快，
新能源汽车企业全球化布局进一步推进，
行业竞争从政策驱动逐步转向产品力、成本和全球化能力竞争。
"""


sources = """
[1]
新能源汽车行业研究资料

[2]
2026年中国新能源汽车行业发展现状、竞争格局及趋势预测
https://www.sohu.com/a/956848374_120113054

[3]
2026年新能源汽车行业全景深度分析
https://m.chinairn.com/scfx/20260814/172707317.shtml
"""


report = generate_report(
    question,
    research_content,
    sources
)


print("\n===== 研究报告 =====\n")

print(report)