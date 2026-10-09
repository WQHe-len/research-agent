import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI


# 从项目环境变量中加载配置
load_dotenv()


def create_llm():
    """创建并返回大语言模型客户端。"""
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv(
        "OPENAI_BASE_URL",
        "https://api.deepseek.com",
    )
    model_name = os.getenv(
        "MODEL_NAME",
        "deepseek-chat",
    )

    if not api_key:
        raise ValueError(
            "未配置 OPENAI_API_KEY，请检查项目根目录下的 .env 文件。"
        )

    return ChatOpenAI(
        model=model_name,
        temperature=0,
        base_url=base_url,
        api_key=api_key,
    )


# 保留现有模块接口，避免修改其他导入 llm 的文件
llm = create_llm()


if __name__ == "__main__":
    # 仅直接运行 python llm.py 时，才发送测试请求
    response = llm.invoke(
        "你好，请用一句话介绍一下你自己。"
    )
    print(response.content)
