
from citation_validator import (
    extract_citation_ids,
    validate_citations,
)


def test_extract_citation_ids():
    report = "市场正在发展 [T1-E1]，技术持续升级 [T2-E3]。"

    result = extract_citation_ids(report)

    assert result == ["T1-E1", "T2-E3"]


def test_duplicate_citations_are_deduplicated():
    report = "结论一 [T1-E1]，结论二 [T1-E1]。"

    result = extract_citation_ids(report)

    assert result == ["T1-E1"]


def test_all_citations_are_valid():
    report = "市场趋势 [T1-E1]。"

    citation_manager = {
        "evidence": [
            {"id": "T1-E1", "content": "测试证据"}
        ]
    }

    result = validate_citations(
        report,
        citation_manager
    )

    assert result["valid"] is True
    assert result["valid_count"] == 1
    assert result["invalid_count"] == 0


def test_unknown_citation_is_invalid():
    report = "市场趋势 [T9-E99]。"

    citation_manager = {
        "evidence": [
            {"id": "T1-E1", "content": "测试证据"}
        ]
    }

    result = validate_citations(
        report,
        citation_manager
    )

    assert result["valid"] is False
    assert result["invalid_citations"] == ["T9-E99"]


def test_report_without_citations():
    result = validate_citations(
        "当前报告没有引用编号。",
        {"evidence": []}
    )

    assert result["valid"] is True
    assert result["citation_count"] == 0