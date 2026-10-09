
from research_pipeline import run_research
from report_exporter import markdown_to_word


def main():

    question = "2026年新能源汽车市场竞争格局"

    print("=" * 60)
    print("Research Agent 回归测试")
    print("=" * 60)

    print(f"\n研究问题：{question}")

    # 1. 运行完整研究流程
    result = run_research(question)

    assert isinstance(result, dict), (
        "失败：研究流程没有返回字典"
    )

    assert not result.get("error"), (
        f"失败：研究流程报错：{result.get('error')}"
    )

    print("\n[PASS] 完整研究流程运行成功")

    # 2. 检查报告
    report = result.get("report", "")

    assert isinstance(report, str) and report.strip(), (
        "失败：没有生成有效报告"
    )

    print(f"[PASS] 报告生成成功，字符数：{len(report)}")

    # 3. 检查 Evidence
    citation_manager = result.get(
        "citation_manager"
    ) or {}

    evidence = citation_manager.get(
        "evidence", []
    )

    print(f"[INFO] Evidence 数量：{len(evidence)}")

    if evidence:
        evidence_ids = [
            item.get("id")
            for item in evidence
            if item.get("id")
        ]

        assert len(evidence_ids) == len(set(evidence_ids)), (
            "失败：发现重复的 Evidence ID"
        )

        print("[PASS] Evidence ID 唯一性检查通过")

    else:
        print("[WARN] 本次没有收集到 Evidence，请检查研究结果")

    # 4. 检查引用校验
    validation = result.get(
        "citation_validation"
    ) or {}

    if validation:
        print(
            "[INFO] 报告引用数量：",
            validation.get("citation_count", 0)
        )

        print(
            "[INFO] 有效引用数量：",
            validation.get("valid_count", 0)
        )

        print(
            "[INFO] 无效引用数量：",
            validation.get("invalid_count", 0)
        )

        assert validation.get("invalid_count", 0) == 0, (
            "失败：报告中存在无法映射的引用编号"
        )

        print("[PASS] 引用编号校验通过")

    else:
        raise AssertionError(
            "失败：研究流程没有返回引用校验结果"
        )

    # 5. 检查 Markdown 导出数据
    assert report.startswith("#"), (
        "提示：报告没有以 Markdown 标题开头，请检查报告格式"
    )

    print("[PASS] Markdown 报告内容检查通过")

    # 6. 检查 Word 导出
    word_file = markdown_to_word(report)

    word_bytes = word_file.getvalue()

    assert word_bytes[:2] == b"PK", (
        "失败：导出的文件不是有效的 DOCX 压缩文档格式"
    )

    print(
        f"[PASS] Word 导出成功，文件大小：{len(word_bytes)} 字节"
    )

    print("\n" + "=" * 60)
    print("回归测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()