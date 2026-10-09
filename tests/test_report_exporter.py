
from io import BytesIO

from docx import Document

from report_exporter import markdown_to_word


def test_markdown_to_word_returns_bytes_io():
    result = markdown_to_word(
        "# 测试报告\n\n这是一段正文。"
    )

    assert isinstance(result, BytesIO)
    assert len(result.getvalue()) > 0


def test_word_document_contains_headings_and_content():
    markdown = (
        "# 测试报告\n\n"
        "## 一、行业概况\n\n"
        "新能源汽车行业正在发展 [T1-E1]。\n\n"
        "- 电池技术\n"
        "- 智能驾驶\n"
    )

    output = markdown_to_word(markdown)

    document = Document(output)

    paragraphs = [
        paragraph.text
        for paragraph in document.paragraphs
    ]

    assert "测试报告" in paragraphs
    assert "一、行业概况" in paragraphs
    assert any(
        "新能源汽车行业正在发展 [T1-E1]" in text
        for text in paragraphs
    )
    assert any("电池技术" in text for text in paragraphs)
    assert any("智能驾驶" in text for text in paragraphs)