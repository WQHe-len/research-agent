import re


def extract_citation_ids(report):
    """
    从最终报告中提取所有类似 [T1-E1] 的引用 ID。
    """

    if not report:
        return []

    pattern = r"\[([A-Za-z0-9]+-E\d+)\]"

    citations = re.findall(
        pattern,
        report
    )

    # 保持出现顺序，同时去重
    unique_citations = []

    for citation in citations:
        if citation not in unique_citations:
            unique_citations.append(citation)

    return unique_citations


def build_evidence_map(citation_manager):
    """
    将 Citation Manager 中的 Evidence
    转换成：

    {
        "T1-E1": {...},
        "T1-E2": {...}
    }
    """

    evidence_map = {}

    if not citation_manager:
        return evidence_map

    evidence_list = citation_manager.get(
        "evidence",
        []
    )

    for evidence in evidence_list:

        evidence_id = evidence.get("id")

        if not evidence_id:
            continue

        evidence_map[evidence_id] = evidence

    return evidence_map


def validate_citations(
    report,
    citation_manager
):
    """
    检查最终报告中的所有 Citation
    是否都对应真实 Evidence。
    """

    citations = extract_citation_ids(
        report
    )

    evidence_map = build_evidence_map(
        citation_manager
    )

    valid_citations = []
    invalid_citations = []

    for citation_id in citations:

        if citation_id in evidence_map:

            valid_citations.append(
                citation_id
            )

        else:

            invalid_citations.append(
                citation_id
            )

    return {
        "valid": len(invalid_citations) == 0,
        "citations": citations,
        "valid_citations": valid_citations,
        "invalid_citations": invalid_citations,
        "citation_count": len(citations),
        "valid_count": len(valid_citations),
        "invalid_count": len(invalid_citations)
    }


def validate_report(
    report,
    citation_manager
):
    """
    对最终报告执行完整引用检查。
    """

    result = validate_citations(
        report,
        citation_manager
    )

    print("\n========================================")
    print("Citation Validator")
    print("========================================")

    print(
        f"检测到引用数量: "
        f"{result['citation_count']}"
    )

    print(
        f"有效引用数量: "
        f"{result['valid_count']}"
    )

    print(
        f"无效引用数量: "
        f"{result['invalid_count']}"
    )

    if result["invalid_citations"]:

        print(
            "\n⚠️ 发现无效 Citation："
        )

        for citation in result[
            "invalid_citations"
        ]:

            print(
                f"  - [{citation}]"
            )

    else:

        print(
            "\n✓ 所有 Citation 均对应有效 Evidence"
        )

    return result