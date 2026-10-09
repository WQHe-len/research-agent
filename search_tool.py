from ddgs import DDGS


def web_search(query):

    results_data = []
    sources = []
    contents = []

    # 用 URL 防止同一次搜索出现完全重复的结果
    seen_urls = set()

    try:

        with DDGS() as ddgs:

            results = ddgs.text(
                query,
                max_results=5
            )

            for item in results:

                title = item.get(
                    "title",
                    ""
                ).strip()

                url = item.get(
                    "href",
                    ""
                ).strip()

                body = item.get(
                    "body",
                    ""
                ).strip()

                # 没有 URL 的结果无法作为可靠引用
                if not url:
                    continue

                # 标题和正文都为空，也没有保留价值
                if not title and not body:
                    continue

                # 去除同一次搜索中的重复 URL
                if url in seen_urls:
                    continue

                seen_urls.add(url)

                # ========================================
                # 保存单条搜索结果
                # ========================================

                result_item = {
                    "title": title,
                    "url": url,
                    "content": body
                }

                results_data.append(
                    result_item
                )

                # ========================================
                # 保留原来的 sources 结构
                # 兼容旧代码
                # ========================================

                sources.append(
                    {
                        "title": title,
                        "url": url
                    }
                )

                # ========================================
                # 保留原来的 content
                # 兼容旧代码
                # ========================================

                if body:
                    contents.append(body)

    except Exception as e:

        print("\n===== Web Search Error =====")
        print(e)

        return {
            "results": [],
            "content": "",
            "sources": [],
            "error": str(e)
        }

    return {
        # 新结构
        "results": results_data,

        # 旧结构，暂时保留
        "content": "\n".join(contents),

        "sources": sources,

        "error": None
    }