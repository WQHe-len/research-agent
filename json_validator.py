import json

from llm import llm


def parse_json(text):
    """
    尝试把 LLM 输出解析成 JSON。

    成功：
        返回 Python dict

    失败：
        返回 None
    """

    if not text:
        return None

    text = text.strip()

    # 情况 1：直接就是合法 JSON
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 情况 2：LLM 在 JSON 外面包了 ```json ... ```
    if "```" in text:

        cleaned = text.replace("```json", "")
        cleaned = cleaned.replace("```JSON", "")
        cleaned = cleaned.replace("```", "")
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            pass

    # 情况 3：JSON 前后混入了解释文字
    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1 and end > start:

        json_text = text[start:end + 1]

        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            pass

    return None


def repair_json(text, schema_description):
    """
    当 LLM 输出不是合法 JSON 时，
    请求 LLM 修复 JSON。

    schema_description:
        告诉 LLM 需要满足什么 JSON 结构。
    """

    prompt = f"""
你是一名 JSON 修复助手。

下面是另一个 AI 模型产生的输出：

===== 原始输出 =====

{text}

===== 要求 =====

请把上面的内容转换成严格合法的 JSON。

必须满足以下结构要求：

{schema_description}

严格要求：

1. 只输出 JSON。
2. 不要输出 Markdown。
3. 不要输出 ```json。
4. 不要添加任何解释文字。
5. 不要改变原始信息的含义。
6. 如果原始内容缺少某个字段，请根据字段要求补充合理的空值。
"""

    response = llm.invoke(prompt)

    return parse_json(response.content)


def parse_with_retry(
    text,
    schema_description,
    max_retries=2
):
    """
    JSON Validator + Retry 主入口。

    流程：

    第一次解析
        ↓
    成功 → 返回
        ↓
    失败
        ↓
    LLM 修复
        ↓
    再次解析
        ↓
    最多重试 max_retries 次
    """

    # 第一次直接解析
    result = parse_json(text)

    if result is not None:
        return {
            "success": True,
            "data": result,
            "retries": 0,
            "error": None
        }

    # Retry / Repair
    for retry in range(1, max_retries + 1):

        print(
            f"\n⚠️ LLM 输出不是合法 JSON，"
            f"正在进行第 {retry} 次修复..."
        )

        result = repair_json(
            text,
            schema_description
        )

        if result is not None:

            print(
                f"✓ JSON 修复成功 "
                f"(第 {retry} 次)"
            )

            return {
                "success": True,
                "data": result,
                "retries": retry,
                "error": None
            }

    return {
        "success": False,
        "data": None,
        "retries": max_retries,
        "error": "LLM 输出无法解析为合法 JSON"
    }