
from json_validator import parse_json


def test_parse_valid_json():
    text = '{"tool": "finish", "answer": "测试成功"}'

    result = parse_json(text)

    assert result == {
        "tool": "finish",
        "answer": "测试成功"
    }


def test_parse_json_with_markdown_fence():
    text = '''```json
{"tool": "finish", "answer": "测试成功"}
```'''

    result = parse_json(text)

    assert result == {
        "tool": "finish",
        "answer": "测试成功"
    }


def test_parse_json_embedded_in_text():
    text = '模型输出如下：{"tool": "finish"} 请继续。'

    result = parse_json(text)

    assert result == {"tool": "finish"}


def test_parse_invalid_json_returns_none():
    result = parse_json('{"tool": ')

    assert result is None


def test_parse_empty_text_returns_none():
    assert parse_json("") is None
    assert parse_json(None) is None