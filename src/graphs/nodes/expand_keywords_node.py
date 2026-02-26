"""
LLM场景拓词节点
根据产品描述和种子关键词生成高转化长尾词
"""
import os
import json
from typing import List, Dict, Any
from jinja2 import Template
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from coze_coding_dev_sdk import LLMClient
from graphs.state import ExpandKeywordsInput, ExpandKeywordsOutput


def expand_keywords_node(
    state: ExpandKeywordsInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> ExpandKeywordsOutput:
    """
    title: 场景化长尾拓词
    desc: 基于产品描述和种子关键词，生成亚马逊真实买家会搜的长尾词，覆盖痛点、场景、使用人群、功能属性等维度
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    # 读取LLM配置
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH", ""), config.get("metadata", {}).get("llm_cfg", ""))
    if not cfg_file or not os.path.exists(cfg_file):
        llm_config = {}
        sp = ""
        up = ""
    else:
        with open(cfg_file, 'r', encoding='utf-8') as fd:
            _cfg = json.load(fd)
        llm_config = _cfg.get("config", {})
        sp = _cfg.get("sp", "")
        up = _cfg.get("up", "")
    
    # 获取输入数据
    product_info: str = state.product_info
    seed_keywords: str = state.seed_keywords
    
    # 渲染用户提示词
    up_tpl = Template(up)
    user_prompt = up_tpl.render({
        "product_description": product_info,  # 使用 product_info 作为产品描述
        "seed_keywords": seed_keywords
    })
    
    # 构建消息
    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt)
    ]
    
    # 调用LLM
    client = LLMClient(ctx=ctx)
    response = client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-8-251228"),
        temperature=llm_config.get("temperature", 0.7),
        max_completion_tokens=llm_config.get("max_completion_tokens", 4096)
    )
    
    # 安全提取响应内容
    content = response.content
    if isinstance(content, str):
        result_text = content
    elif isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
            elif isinstance(item, str):
                text_parts.append(item)
        result_text = " ".join(text_parts)
    else:
        result_text = str(content)
    
    return ExpandKeywordsOutput(longtail_keywords=result_text)
