
import streamlit as st

from research_pipeline import run_research
from report_exporter import markdown_to_word


# ==============================
# 1. 页面配置
# ==============================

st.set_page_config(
    page_title="Research Agent",
    page_icon="🔎",
    layout="wide"
)


# ==============================
# 2. 页面标题
# ==============================

st.title("🔎 Research Agent")

st.caption(
    "AI 行业研究助手：从研究规划、资料检索到报告生成与引用校验"
)

st.divider()


# ==============================
# 3. 输入研究主题
# ==============================

st.subheader("开始一项研究")

question = st.text_area(
    "你想研究什么问题？",
    placeholder="例如：2026年新能源汽车市场竞争格局",
    height=100
)

start_button = st.button(
    "🚀 开始研究",
    type="primary",
    use_container_width=True
)


# ==============================
# 4. 执行研究流程
# ==============================

if start_button:

    if not question.strip():

        st.warning("请先输入一个研究主题。")

    else:

        try:

            with st.spinner(
                "正在研究中：规划任务、搜索资料、整理证据并生成报告……"
            ):

                result = run_research(
                    question.strip()
                )

            if not isinstance(result, dict):

                st.error(
                    "研究流程返回的数据格式不正确。"
                )

            elif result.get("error"):

                st.error(
                    f"研究流程未能完成：{result['error']}"
                )

            else:

                st.session_state["research_result"] = result

                st.session_state["research_question"] = (
                    question.strip()
                )

                st.success("研究完成！")

        except Exception as e:

            st.error(
                f"运行过程中发生异常：{e}"
            )


# ==============================
# 5. 展示研究结果
# ==============================

result = st.session_state.get(
    "research_result"
)


if result:

    st.divider()

    st.header("📊 研究结果")


    # ==============================
    # 5.1 研究概况
    # ==============================

    plan = result.get("plan") or {}

    tasks = plan.get("tasks", [])

    citation_manager = (
        result.get("citation_manager") or {}
    )

    evidence = citation_manager.get(
        "evidence", []
    )

    sources = citation_manager.get(
        "sources", []
    )

    validation = (
        result.get("citation_validation") or {}
    )


    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "研究子任务",
        len(tasks)
    )

    col2.metric(
        "Evidence 证据",
        len(evidence)
    )

    col3.metric(
        "来源数量",
        len(sources)
    )

    col4.metric(
        "无效引用",
        validation.get("invalid_count", 0)
    )


    # ==============================
    # 5.2 标签页
    # ==============================

    (
        tab_report,
        tab_plan,
        tab_evidence,
        tab_validation
    ) = st.tabs(
        [
            "📄 研究报告",
            "🗂️ 研究计划",
            "🔗 证据与来源",
            "✅ 引用校验"
        ]
    )


    # ==============================
    # 6. 研究报告与文件导出
    # ==============================

    with tab_report:

        report = result.get("report", "")

        if report:

            st.markdown(report)

            st.divider()

            st.subheader("📥 下载研究报告")

            col_md, col_word = st.columns(2)


            # ---------- Markdown 导出 ----------

            with col_md:

                st.download_button(
                    label="下载 Markdown 报告",
                    data=report,
                    file_name="research_report.md",
                    mime="text/markdown",
                    use_container_width=True,
                    key="download_markdown"
                )


            # ---------- Word 导出 ----------

            with col_word:

                try:

                    word_file = markdown_to_word(
                        report
                    )

                    st.download_button(
                        label="下载 Word 报告",
                        data=word_file.getvalue(),
                        file_name="research_report.docx",
                        mime=(
                            "application/vnd.openxmlformats-officedocument."
                            "wordprocessingml.document"
                        ),
                        use_container_width=True,
                        key="download_word"
                    )

                except Exception as e:

                    st.error(
                        f"Word 报告生成失败：{e}"
                    )

        else:

            st.warning(
                "本次研究没有生成报告。"
            )


    # ==============================
    # 7. 研究计划
    # ==============================

    with tab_plan:

        st.subheader(
            "Planner 生成的研究计划"
        )

        st.write(
            plan.get(
                "question",
                result.get("question", "")
            )
        )


        if tasks:

            for task in tasks:

                task_id = task.get(
                    "id", ""
                )

                task_name = task.get(
                    "task", "未命名任务"
                )

                with st.expander(
                    f"任务 {task_id}：{task_name}",
                    expanded=False
                ):

                    st.write(
                        "**研究目的：**",
                        task.get(
                            "purpose",
                            "未提供"
                        )
                    )

        else:

            st.info(
                "没有可展示的研究子任务。"
            )


        # ---------- 子任务执行情况 ----------

        research_results = result.get(
            "research_results", []
        )

        if research_results:

            st.subheader(
                "子任务执行情况"
            )

            for item in research_results:

                task_name = item.get(
                    "task",
                    "研究子任务"
                )

                with st.expander(
                    task_name,
                    expanded=False
                ):

                    st.write(
                        item.get(
                            "summary",
                            "暂无摘要"
                        )
                    )

                    limitations = item.get(
                        "limitations", []
                    )

                    if limitations:

                        st.write(
                            "**研究限制：**"
                        )

                        for limitation in limitations:

                            st.write(
                                f"- {limitation}"
                            )


    # ==============================
    # 8. Evidence 与来源
    # ==============================

    with tab_evidence:

        st.subheader(
            "Evidence 证据库"
        )

        if evidence:

            for item in evidence:

                title = item.get(
                    "title",
                    "未命名证据"
                )

                evidence_id = item.get(
                    "id",
                    "未知 ID"
                )

                with st.expander(
                    f"[{evidence_id}] {title}",
                    expanded=False
                ):

                    st.write(
                        "**证据类型：**",
                        item.get(
                            "type",
                            "未知"
                        )
                    )

                    st.write(
                        "**所属研究任务：**",
                        item.get(
                            "task_id",
                            "未关联"
                        )
                    )

                    st.write(
                        "**检索问题：**",
                        item.get(
                            "query",
                            "无"
                        )
                    )

                    url = item.get(
                        "url",
                        ""
                    )

                    if url:

                        st.markdown(
                            f"[打开原始来源]({url})"
                        )

                    st.write(
                        "**证据内容：**"
                    )

                    st.write(
                        item.get(
                            "content",
                            "暂无内容"
                        )
                    )

        else:

            st.info(
                "本次研究没有收集到 Evidence。"
            )


        st.divider()

        st.subheader(
            "去重后的来源列表"
        )

        if sources:

            for source in sources:

                title = source.get(
                    "title",
                    "未命名来源"
                )

                url = source.get(
                    "url",
                    ""
                )

                if url:

                    st.markdown(
                        f"- [{title}]({url})"
                    )

                else:

                    st.write(
                        f"- {title}"
                    )

        else:

            st.info(
                "没有可展示的外部来源。"
            )


    # ==============================
    # 9. 引用校验
    # ==============================

    with tab_validation:

        st.subheader(
            "Final Citation Validator"
        )

        if validation:

            if validation.get(
                "valid",
                False
            ):

                st.success(
                    "所有检测到的引用都能对应到 Evidence。"
                )

            else:

                st.warning(
                    "发现无效引用，请检查报告中的引用编号。"
                )


            c1, c2, c3 = st.columns(3)

            c1.metric(
                "引用数量",
                validation.get(
                    "citation_count",
                    0
                )
            )

            c2.metric(
                "有效引用",
                validation.get(
                    "valid_count",
                    0
                )
            )

            c3.metric(
                "无效引用",
                validation.get(
                    "invalid_count",
                    0
                )
            )


            invalid_citations = validation.get(
                "invalid_citations",
                []
            )

            if invalid_citations:

                st.write(
                    "**无效引用编号：**"
                )

                for citation in invalid_citations:

                    st.write(
                        f"- `{citation}`"
                    )


            with st.expander(
                "查看全部引用编号"
            ):

                st.write(
                    validation.get(
                        "citations",
                        []
                    )
                )

        else:

            st.info(
                "当前结果没有提供引用校验数据。"
            )


# ==============================
# 10. 页面底部
# ==============================

st.divider()

st.caption(
    "Research Agent · AI 行业研究助手"
)