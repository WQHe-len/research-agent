from research_pipeline import run_research


def main():

    print("=" * 60)
    print("Research Agent Pipeline Test")
    print("=" * 60)

    question = input(
        "\n请输入研究问题："
    ).strip()

    if not question:
        print("研究问题不能为空。")
        return

    result = run_research(question)

    print("\n")
    print("=" * 60)
    print("最终研究报告")
    print("=" * 60)

    report = result.get(
        "report",
        ""
    )

    if report:
        print(report)
    else:
        print("未生成研究报告。")

    print("\n")
    print("=" * 60)
    print("研究系统统计")
    print("=" * 60)

    citation_manager = result.get(
        "citation_manager",
        {}
    )

    findings = citation_manager.get(
        "findings",
        []
    )

    evidence = citation_manager.get(
        "evidence",
        []
    )

    sources = citation_manager.get(
        "sources",
        []
    )

    print(
        f"Findings 数量：{len(findings)}"
    )

    print(
        f"Evidence 数量：{len(evidence)}"
    )

    print(
        f"Source 数量：{len(sources)}"
    )


if __name__ == "__main__":
    main()