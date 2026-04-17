"""LangGraph 版 LLM 服务模块（兼容 DeepSeek / OpenAI 等接口）"""

import os
from langchain_openai import ChatOpenAI
from ..config import get_settings

# 两个单例：工具调用节点用 temperature=0，规划/编辑节点用 temperature=0.7
_llm_tool: ChatOpenAI | None = None      # 景点/天气/酒店节点：事实查询，确定性优先
_llm_creative: ChatOpenAI | None = None  # planner/edit 节点：生成行程，需要一定创意


def _build_llm(temperature: float) -> ChatOpenAI:
    """根据配置构造 ChatOpenAI 实例（内部复用，避免重复读取环境变量）"""
    settings = get_settings()
    api_key  = os.getenv("LLM_API_KEY")  or os.getenv("OPENAI_API_KEY")  or settings.openai_api_key
    base_url = os.getenv("LLM_BASE_URL") or os.getenv("OPENAI_BASE_URL") or settings.openai_base_url
    model    = os.getenv("LLM_MODEL_ID") or os.getenv("OPENAI_MODEL")    or settings.openai_model
    return ChatOpenAI(api_key=api_key, base_url=base_url, model=model, temperature=temperature)


def get_llm_lg() -> ChatOpenAI:
    """
    获取创意型 LLM 实例（temperature=0.7），单例。
    用于 planner_node / edit_node：需要语言流畅、行程描述有变化。
    """
    global _llm_creative
    if _llm_creative is None:
        _llm_creative = _build_llm(temperature=0.7)
        settings = get_settings()
        model = os.getenv("LLM_MODEL_ID") or os.getenv("OPENAI_MODEL") or settings.openai_model
        print(f"✅ LLM 初始化（creative, temperature=0.7）模型: {model}")
    return _llm_creative


def get_llm_tool() -> ChatOpenAI:
    """
    获取工具调用型 LLM 实例（temperature=0），单例。
    用于 attraction_node / weather_node / hotel_node：
    事实性工具调用，temperature=0 输出更稳定、减少幻觉。
    """
    global _llm_tool
    if _llm_tool is None:
        _llm_tool = _build_llm(temperature=0)
        settings = get_settings()
        model = os.getenv("LLM_MODEL_ID") or os.getenv("OPENAI_MODEL") or settings.openai_model
        print(f"✅ LLM 初始化（tool, temperature=0）模型: {model}")
    return _llm_tool
