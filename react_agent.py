import json

from llm import llm

from tools import (
    knowledge_search,
    calculator
)

from search_tool import web_search

from json_validator import parse_with_retry


TOOLS = {
    "knowledge_search": knowledge_search,
    "calculator": calculator,
    "web_search": web_search
}


def deduplicate_sources(sources):
    """
    对来源去重。
    使用 URL 作为主要判断依据。
    """

    unique_sources = []
    seen_urls = set()

    for source in sources:

        url = source.get(
            "url",
            ""
        )

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        unique_sources.append(source)

    return unique_sources


def research_task(question, task):

    memory = {
        "history": "",
        "sources": [],
        "evidence": []
    }

    # ========================================
    # Citation Manager 2.1
    # URL -> Evidence ID
    # ========================================

    evidence_by_url = {}

    search_count = 0
    max_searches = 3

    print("\n========================================")
    print("Research Task")
    print("========================================")
    print(f"主问题：{question}")
    print(f"当前任务：{task}")

    # ========================================
    # Research Loop
    # ========================================

    for step in range(5):

        prompt = f"""
你是一个专业的 Research Agent。

你的职责不是直接回答整个用户问题，
而是负责完成一个具体的研究子任务。

你可以使用三个工具：

knowledge_search：
查询本地新能源汽车行业知识库。

web_search：
搜索互联网最新信息。

calculator：
执行数学计算。

==============================
工具选择规则
==============================

1.
如果子任务涉及本地行业基础知识，
优先使用 knowledge_search。

2.
如果子任务涉及最新市场数据、新闻、政策、
企业动态或2026年的信息，
使用 web_search。

3.
如果涉及数学计算，
使用 calculator。

4.
如果需要同时使用多个工具，
可以分步骤调用。

5.
只有在当前研究子任务已经获得足够证据后，
才能返回 finish。

==============================
重要研究原则
==============================

1.
只研究当前子任务。

2.
不要试图完成整个用户问题。

3.
不要提前生成最终研究报告。

4.
不要编造数据。

5.
不要编造来源。

6.
如果资料不足，要明确指出。

7.
网络信息和本地知识库信息要区分。

8.
研究过程应该以事实、数据、证据为主。

9.
如果网络搜索失败，不要假设搜索成功。

10.
如果已经获得足够信息，就应该 finish。

==============================
网络搜索预算
==============================

本任务最多进行 {max_searches} 次 web_search。

当前已经使用：

{search_count} 次。

如果已经达到搜索上限，
不要继续调用 web_search。

==============================
finish 输出格式
==============================

如果需要调用工具：

{{
    "thought": "为什么需要调用这个工具",
    "tool": "工具名称",
    "input": "工具输入"
}}

如果当前子任务已经研究完成：

{{
    "thought": "为什么当前子任务已经有足够信息",

    "tool": "finish",

    "summary": "当前研究任务的简洁总结",

    "key_findings": [
        {{
            "finding": "关键研究发现",
            "evidence_ids": ["E1", "E2"]
        }},
        {{
            "finding": "另一个关键研究发现",
            "evidence_ids": ["E3"]
        }}
    ],

    "limitations": [
        "当前研究存在的限制"
    ]
}}

==============================
Citation 规则
==============================

每一条 key_finding 都必须尽可能关联 evidence_ids。

evidence_ids 必须来自已经获得的研究证据。

不能编造 evidence_id。

如果某个 finding 没有可靠证据支持，
不要把它写成确定事实。

例如：

{{
    "finding": "2026年新能源汽车渗透率继续提升",
    "evidence_ids": ["E1", "E3"]
}}

而不是：

{{
    "finding": "2026年新能源汽车渗透率继续提升",
    "evidence_ids": []
}}

如果确实没有证据，
应该将这个信息放入 limitations，
而不是编造引用。

==============================
Evidence 列表
==============================

下面是当前研究过程中已经获得的证据：

{json.dumps(
    memory["evidence"],
    ensure_ascii=False,
    indent=2
)}

==============================
用户总问题
==============================

{question}

==============================
当前研究子任务
==============================

{task}

==============================
之前的研究过程
==============================

{memory["history"]}
"""

        # ========================================
        # 调用 LLM
        # ========================================

        response = llm.invoke(prompt)

        text = response.content.strip()

        print("\n===== Research Agent Step =====")
        print(text)

        # ========================================
        # JSON Validator + Retry
        # ========================================

        schema_description = """
如果调用工具：

{
    "thought": "为什么需要调用这个工具",
    "tool": "knowledge_search 或 web_search 或 calculator",
    "input": "工具输入"
}

如果研究完成：

{
    "thought": "为什么当前子任务已经有足够信息",
    "tool": "finish",
    "summary": "当前研究任务的简洁总结",
    "key_findings": [
        {
            "finding": "关键研究发现",
            "evidence_ids": ["E1", "E2"]
        }
    ],
    "limitations": [
        "当前研究存在的限制"
    ]
}
"""

        validation_result = parse_with_retry(
            text,
            schema_description,
            max_retries=2
        )

        # ========================================
        # JSON 修复失败
        # ========================================

        if not validation_result["success"]:

            print(
                "\n❌ Research Agent JSON 修复失败。"
            )

            return {
                "task": task,

                "summary": "",

                "key_findings": [],

                "limitations": [
                    "Research Agent 输出无法解析为合法 JSON。"
                ],

                "evidence": memory["evidence"],

                "sources": deduplicate_sources(
                    memory["sources"]
                ),

                "history": memory["history"],

                "error": text
            }

        action = validation_result["data"]

        # ========================================
        # JSON 类型检查
        # ========================================

        if not isinstance(
            action,
            dict
        ):

            print(
                "\n❌ Research Agent JSON 不是对象结构。"
            )

            return {
                "task": task,

                "summary": "",

                "key_findings": [],

                "limitations": [
                    "Research Agent 输出的 JSON 结构不是对象。"
                ],

                "evidence": memory["evidence"],

                "sources": deduplicate_sources(
                    memory["sources"]
                ),

                "history": memory["history"],

                "error": text
            }

        # ========================================
        # 如果发生了 JSON Retry
        # ========================================

        if validation_result["retries"] > 0:

            print(
                f"\n✓ Research Agent JSON "
                f"经过 {validation_result['retries']} 次修复后通过验证。"
            )

        # ========================================
        # 获取 Tool
        # ========================================

        tool = action.get(
            "tool"
        )

        # ========================================
        # Research 完成
        # ========================================

        if tool == "finish":

            summary = action.get(
                "summary",
                ""
            )

            key_findings = action.get(
                "key_findings",
                []
            )

            limitations = action.get(
                "limitations",
                []
            )

            # ------------------------------------
            # 类型保护
            # ------------------------------------

            if not isinstance(
                key_findings,
                list
            ):

                key_findings = []

            if not isinstance(
                limitations,
                list
            ):

                limitations = [
                    str(limitations)
                ]

            # ------------------------------------
            # 验证 Evidence ID
            # ------------------------------------

            valid_evidence_ids = {
                evidence["id"]
                for evidence in memory["evidence"]
            }

            validated_findings = []

            for finding in key_findings:

                # -------------------------------
                # 如果 LLM 返回字符串
                # -------------------------------

                if isinstance(
                    finding,
                    str
                ):

                    validated_findings.append(
                        {
                            "finding": finding,
                            "evidence_ids": []
                        }
                    )

                    continue

                # -------------------------------
                # 如果不是 dict
                # -------------------------------

                if not isinstance(
                    finding,
                    dict
                ):

                    continue

                finding_text = finding.get(
                    "finding",
                    ""
                )

                evidence_ids = finding.get(
                    "evidence_ids",
                    []
                )

                if not isinstance(
                    evidence_ids,
                    list
                ):

                    evidence_ids = []

                # -------------------------------
                # 只保留真实存在的 Evidence ID
                # -------------------------------

                evidence_ids = [
                    evidence_id
                    for evidence_id in evidence_ids
                    if evidence_id in valid_evidence_ids
                ]

                validated_findings.append(
                    {
                        "finding": finding_text,
                        "evidence_ids": evidence_ids
                    }
                )

            # ====================================
            # Research Task Complete
            # ====================================

            print(
                "\n===== Research Task Complete ====="
            )

            print(
                "\n【Summary】"
            )

            print(summary)

            print(
                "\n【Key Findings】"
            )

            for finding in validated_findings:

                print(
                    f"- {finding['finding']}"
                )

                print(
                    f"  Evidence: "
                    f"{finding['evidence_ids']}"
                )

            print(
                "\n【Limitations】"
            )

            for limitation in limitations:

                print(
                    f"- {limitation}"
                )

            return {
                "task": task,

                "summary": summary,

                "key_findings": validated_findings,

                "limitations": limitations,

                "evidence": memory["evidence"],

                "sources": deduplicate_sources(
                    memory["sources"]
                ),

                "history": memory["history"]
            }

        # ========================================
        # 调用工具
        # ========================================

        if tool in TOOLS:

            tool_input = action.get(
                "input",
                ""
            )

            # ====================================
            # Web Search
            # ====================================

            if tool == "web_search":

                if search_count >= max_searches:

                    print(
                        "\nWeb Search 已达到本任务最大次数。"
                    )

                    memory["history"] += f"""
================================
研究限制
================================

Web Search 已达到最大次数
{max_searches} 次。

Research Agent 无法继续进行网络搜索，
需要基于目前已经获得的信息完成研究。

"""

                    continue

                search_count += 1

                print(
                    f"\nWeb Search "
                    f"{search_count}/{max_searches}"
                )

                result = TOOLS[tool](
                    tool_input
                )

                # --------------------------------
                # Citation Manager 2.1
                # 优先使用结构化 results
                # --------------------------------

                structured_results = result.get(
                    "results",
                    []
                )

                web_sources = result.get(
                    "sources",
                    []
                )

                search_error = result.get(
                    "error"
                )

                tool_contents = []

                # ====================================
                # 新版 Search Tool
                # 一条搜索结果 = 一个 Evidence
                # ====================================

                if structured_results:

                    for item in structured_results:

                        title = item.get(
                            "title",
                            ""
                        ).strip()

                        url = item.get(
                            "url",
                            ""
                        ).strip()

                        content = item.get(
                            "content",
                            ""
                        ).strip()

                        # ----------------------------
                        # 无 URL 不作为 Web Evidence
                        # ----------------------------

                        if not url:
                            continue

                        # ----------------------------
                        # URL 去重
                        # ----------------------------

                        if url in evidence_by_url:

                            existing_id = evidence_by_url[
                                url
                            ]

                            print(
                                "\n发现重复 Evidence："
                            )

                            print(
                                f"URL：{url}"
                            )

                            print(
                                f"复用：{existing_id}"
                            )

                            continue

                        # ----------------------------
                        # 创建 Evidence
                        # ----------------------------

                        evidence_id = (
                            f"E{len(memory['evidence']) + 1}"
                        )

                        evidence = {
                            "id": evidence_id,

                            "type": "web",

                            "title": title,

                            "url": url,

                            "query": tool_input,

                            "content": content
                        }

                        memory["evidence"].append(
                            evidence
                        )

                        evidence_by_url[
                            url
                        ] = evidence_id

                        tool_contents.append(
                            content
                        )

                        # ----------------------------
                        # 保存 Source
                        # ----------------------------

                        memory["sources"].append(
                            {
                                "title": title,
                                "url": url
                            }
                        )

                # ====================================
                # 兼容旧版 Search Tool
                # ====================================

                else:

                    for source in web_sources:

                        title = source.get(
                            "title",
                            ""
                        ).strip()

                        url = source.get(
                            "url",
                            ""
                        ).strip()

                        if not url:
                            continue

                        # ----------------------------
                        # URL 去重
                        # ----------------------------

                        if url in evidence_by_url:

                            existing_id = evidence_by_url[
                                url
                            ]

                            print(
                                "\n发现重复 Evidence："
                            )

                            print(
                                f"URL：{url}"
                            )

                            print(
                                f"复用：{existing_id}"
                            )

                            continue

                        evidence_id = (
                            f"E{len(memory['evidence']) + 1}"
                        )

                        evidence = {
                            "id": evidence_id,

                            "type": "web",

                            "title": title,

                            "url": url,

                            "query": tool_input,

                            "content": result.get(
                                "content",
                                ""
                            )
                        }

                        memory["evidence"].append(
                            evidence
                        )

                        evidence_by_url[
                            url
                        ] = evidence_id

                        memory["sources"].append(
                            {
                                "title": title,
                                "url": url
                            }
                        )

                # ====================================
                # Tool Result
                # ====================================

                if tool_contents:

                    tool_result = "\n\n".join(
                        tool_contents
                    )

                else:

                    tool_result = result.get(
                        "content",
                        ""
                    )

                # ====================================
                # 搜索错误处理
                # ====================================

                if search_error:

                    tool_result += f"""
本次网络搜索失败。

错误信息：

{search_error}

请不要假设搜索成功。
"""

            # ====================================
            # Knowledge Search
            # ====================================

            elif tool == "knowledge_search":

                result = TOOLS[tool](
                    tool_input
                )

                tool_result = result

                evidence_id = (
                    f"E{len(memory['evidence']) + 1}"
                )

                memory["evidence"].append(
                    {
                        "id": evidence_id,

                        "type": "knowledge_base",

                        "title": "本地新能源汽车行业知识库",

                        "url": "",

                        "query": tool_input,

                        "content": str(
                            tool_result
                        )
                    }
                )

            # ====================================
            # Calculator
            # ====================================

            else:

                result = TOOLS[tool](
                    tool_input
                )

                tool_result = result

                evidence_id = (
                    f"E{len(memory['evidence']) + 1}"
                )

                memory["evidence"].append(
                    {
                        "id": evidence_id,

                        "type": "calculation",

                        "title": "Calculator",

                        "url": "",

                        "query": tool_input,

                        "content": str(
                            tool_result
                        )
                    }
                )

            # ====================================
            # 保存研究过程
            # ====================================

            memory["history"] += f"""
================================
研究步骤
================================

工具：

{tool}

工具输入：

{tool_input}

工具结果：

{tool_result}

"""

        # ========================================
        # 未知工具
        # ========================================

        else:

            return {
                "task": task,

                "summary": "",

                "key_findings": [],

                "limitations": [
                    f"Research Agent 调用了未知工具：{tool}"
                ],

                "evidence": memory["evidence"],

                "sources": deduplicate_sources(
                    memory["sources"]
                ),

                "history": memory["history"],

                "error": f"未知工具：{tool}"
            }

    # ========================================
    # 超过最大步骤
    # ========================================

    return {
        "task": task,

        "summary": "",

        "key_findings": [],

        "limitations": [
            "Research Agent 超过最大研究步骤限制，"
            "未能正常完成研究。"
        ],

        "evidence": memory["evidence"],

        "sources": deduplicate_sources(
            memory["sources"]
        ),

        "history": memory["history"],

        "error": "研究步骤超过最大限制"
    }


def react_agent(question):

    task = question

    result = research_task(
        question=question,
        task=task
    )

    return result