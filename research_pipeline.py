from planner import create_plan
from react_agent import research_task
from report_writer import generate_report
from citation_validator import validate_report


def deduplicate_sources(sources):
    """
    根据 URL 对来源进行去重。
    """

    unique_sources = []
    seen_urls = set()

    for source in sources:

        url = source.get("url", "")

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)

        unique_sources.append(source)

    return unique_sources


def build_citation_manager(research_results):
    """
    将所有 Research Agent 的 Evidence
    汇总成统一的 Citation Manager。

    同时把每个任务内部的 Evidence ID：

        E1
        E2
        E3

    转换成全局唯一 ID：

        T1-E1
        T1-E2
        T2-E1
        T2-E2
    """

    all_evidence = []
    all_findings = []
    all_sources = []

    global_evidence_map = {}

    for result in research_results:

        task_id = result.get(
            "task_id",
            0
        )

        evidence_list = result.get(
            "evidence",
            []
        )

        # ==============================
        # Evidence
        # ==============================

        local_to_global = {}

        for evidence in evidence_list:

            local_id = evidence.get(
                "id"
            )

            if not local_id:
                continue

            global_id = (
                f"T{task_id}-{local_id}"
            )

            local_to_global[
                local_id
            ] = global_id

            new_evidence = {
                "id": global_id,
                "type": evidence.get(
                    "type",
                    ""
                ),
                "title": evidence.get(
                    "title",
                    ""
                ),
                "url": evidence.get(
                    "url",
                    ""
                ),
                "query": evidence.get(
                    "query",
                    ""
                ),
                "content": evidence.get(
                    "content",
                    ""
                ),
                "task_id": task_id
            }

            all_evidence.append(
                new_evidence
            )

            global_evidence_map[
                global_id
            ] = new_evidence

        # ==============================
        # Findings
        # ==============================

        findings = result.get(
            "key_findings",
            []
        )

        for finding in findings:

            finding_text = finding.get(
                "finding",
                ""
            )

            local_evidence_ids = (
                finding.get(
                    "evidence_ids",
                    []
                )
            )

            global_evidence_ids = []

            for local_id in local_evidence_ids:

                global_id = local_to_global.get(
                    local_id
                )

                if global_id:

                    global_evidence_ids.append(
                        global_id
                    )

            all_findings.append(
                {
                    "task_id": task_id,
                    "finding": finding_text,
                    "evidence_ids": global_evidence_ids
                }
            )

        # ==============================
        # Sources
        # ==============================

        sources = result.get(
            "sources",
            []
        )

        all_sources.extend(
            sources
        )

    # ==============================
    # Sources 去重
    # ==============================

    all_sources = deduplicate_sources(
        all_sources
    )

    # ==============================
    # Citation Manager
    # ==============================

    citation_manager = {
        "findings": all_findings,
        "evidence": all_evidence,
        "sources": all_sources
    }

    return citation_manager


def build_research_memory(
    question,
    research_results,
    citation_manager
):
    """
    构建 Research Memory。

    Research Memory 负责把多个 Research Agent
    的结果整理成结构化研究记忆，
    供 Report Writer 使用。
    """

    sections = []

    for result in research_results:

        task_id = result.get(
            "task_id"
        )

        task = result.get(
            "task",
            ""
        )

        purpose = result.get(
            "purpose",
            ""
        )

        summary = result.get(
            "summary",
            ""
        )

        key_findings = result.get(
            "key_findings",
            []
        )

        limitations = result.get(
            "limitations",
            []
        )

        sections.append(
            {
                "id": task_id,
                "task": task,
                "purpose": purpose,
                "summary": summary,
                "key_findings": key_findings,
                "limitations": limitations
            }
        )

    research_memory = {
        "question": question,
        "sections": sections,
        "citation_manager": citation_manager
    }

    return research_memory


def run_research(question):
    """
    完整 Research Pipeline：

    1. Planner
    2. Research Agents
    3. Citation Manager
    4. Research Memory
    5. Report Writer
    6. Citation Validator
    """

    print("\n========================================")
    print("Research Pipeline")
    print("========================================")

    print(
        f"\n研究问题：{question}"
    )

    # ==================================================
    # Step 1：Planner
    # ==================================================

    print("\n========================================")
    print("Step 1：Planner")
    print("========================================")

    plan = create_plan(
        question
    )

    if not plan:

        print(
            "\n⚠️ Planner 没有生成有效计划。"
        )

        return {
            "question": question,
            "plan": None,
            "research_results": [],
            "research_memory": None,
            "citation_manager": None,
            "report": None,
            "citation_validation": None,
            "error": "Planner 执行失败"
        }

    tasks = plan.get(
        "tasks",
        []
    )

    print(
        f"\nPlanner 生成 "
        f"{len(tasks)} 个研究任务。"
    )

    # ==================================================
    # Step 2：Research Agents
    # ==================================================

    print("\n========================================")
    print("Step 2：Research Agents")
    print("========================================")

    research_results = []

    for task_info in tasks:

        task_id = task_info.get(
            "id"
        )

        task_text = task_info.get(
            "task",
            ""
        )

        purpose = task_info.get(
            "purpose",
            ""
        )

        print(
            f"\n----------------------------------------"
        )

        print(
            f"Research Task {task_id}"
        )

        print(
            f"任务：{task_text}"
        )

        try:

            result = research_task(
                question,
                task_text
            )

        except Exception as e:

            print(
                f"\n⚠️ Research Task "
                f"{task_id} 执行失败："
            )

            print(e)

            result = {
                "task_id": task_id,
                "task": task_text,
                "purpose": purpose,
                "summary": (
                    "该研究子任务执行失败，"
                    "未能获得完整研究结果。"
                ),
                "key_findings": [],
                "limitations": [
                    (
                        "Research Agent 执行过程中"
                        f"发生异常：{str(e)}"
                    )
                ],
                "evidence": [],
                "sources": [],
                "history": ""
            }

        # 补充 Pipeline 层面的任务信息

        result["task_id"] = task_id
        result["task"] = task_text
        result["purpose"] = purpose

        research_results.append(
            result
        )

    print(
        f"\nResearch Agents 完成："
        f"{len(research_results)} 个任务"
    )

    # ==================================================
    # Step 3：Citation Manager
    # ==================================================

    print("\n========================================")
    print("Step 3：Citation Manager")
    print("========================================")

    citation_manager = build_citation_manager(
        research_results
    )

    evidence_count = len(
        citation_manager.get(
            "evidence",
            []
        )
    )

    finding_count = len(
        citation_manager.get(
            "findings",
            []
        )
    )

    source_count = len(
        citation_manager.get(
            "sources",
            []
        )
    )

    print(
        f"\nEvidence 数量：{evidence_count}"
    )

    print(
        f"Finding 数量：{finding_count}"
    )

    print(
        f"Source 数量：{source_count}"
    )

    # ==================================================
    # Step 4：Research Memory
    # ==================================================

    print("\n========================================")
    print("Step 4：Research Memory")
    print("========================================")

    research_memory = build_research_memory(
        question,
        research_results,
        citation_manager
    )

    section_count = len(
        research_memory.get(
            "sections",
            []
        )
    )

    print(
        f"\nResearch Memory 构建完成："
        f"{section_count} 个研究模块"
    )

    # ==================================================
    # Step 5：Report Writer
    # ==================================================

    print("\n========================================")
    print("Step 5：Report Writer")
    print("========================================")

    try:

        report = generate_report(
            question,
            research_memory
        )

    except Exception as e:

        print(
            "\n⚠️ Report Writer 执行失败："
        )

        print(e)

        return {
            "question": question,
            "plan": plan,
            "research_results": research_results,
            "research_memory": research_memory,
            "citation_manager": citation_manager,
            "report": None,
            "citation_validation": None,
            "error": (
                f"Report Writer 执行失败：{str(e)}"
            )
        }

    print(
        "\n✓ Report Writer 完成"
    )

    # ==================================================
    # Step 6：Final Citation Validator
    # ==================================================

    print("\n========================================")
    print("Step 6：Final Citation Validator")
    print("========================================")

    try:

        citation_validation = validate_report(
            report,
            citation_manager
        )

    except Exception as e:

        print(
            "\n⚠️ Citation Validator 执行失败："
        )

        print(e)

        citation_validation = {
            "valid": False,
            "citations": [],
            "valid_citations": [],
            "invalid_citations": [],
            "citation_count": 0,
            "valid_count": 0,
            "invalid_count": 0,
            "error": str(e)
        }

    # ==================================================
    # Pipeline Summary
    # ==================================================

    print("\n========================================")
    print("Research Pipeline 完成")
    print("========================================")

    print(
        f"Evidence：{evidence_count}"
    )

    print(
        f"Findings：{finding_count}"
    )

    print(
        f"Sources：{source_count}"
    )

    print(
        f"报告引用数量："
        f"{citation_validation.get('citation_count', 0)}"
    )

    print(
        f"有效引用："
        f"{citation_validation.get('valid_count', 0)}"
    )

    print(
        f"无效引用："
        f"{citation_validation.get('invalid_count', 0)}"
    )

    if citation_validation.get("valid"):

        print(
            "\n✓ Final Citation Validation 通过"
        )

    else:

        print(
            "\n⚠️ Final Citation Validation "
            "发现问题"
        )

    # ==================================================
    # Final Result
    # ==================================================

    return {
        "question": question,
        "plan": plan,
        "research_results": research_results,
        "research_memory": research_memory,
        "citation_manager": citation_manager,
        "report": report,
        "citation_validation": citation_validation,
        "error": None
    }