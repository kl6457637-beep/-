"""
LLM语义相关性判断节点
判断剩余词是否与产品无关（品类错配、属性冲突）
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
from graphs.state import SemanticJudgeInput, SemanticJudgeOutput


def semantic_judge_node(
    state: SemanticJudgeInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SemanticJudgeOutput:
    """
    title: 语义相关性判断
    desc: 使用大模型判断剩余关键词是否与产品不相关，识别品类错误和属性冲突的词
    integrations: 大语言模型
    """
    ctx = runtime.context
    
    # 读取LLM配置
    cfg_file = os.path.join(os.getenv("COZE_WORKSPACE_PATH", ""), config.get("metadata", {}).get("llm_cfg", ""))
    if not cfg_file or not os.path.exists(cfg_file):
        # 使用默认配置
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
    remaining_keywords: List[Dict[str, Any]] = state.remaining_keywords
    product_info: str = state.product_info
    
    if not remaining_keywords:
        return SemanticJudgeOutput(semantic_bad="")
    
    # 构建搜索词列表
    keywords_text = "\n".join([
        item.get("search_term", "") 
        for item in remaining_keywords 
        if item.get("search_term")
    ])
    
    # 渲染用户提示词
    up_tpl = Template(up)
    user_prompt = up_tpl.render({
        "product_info": product_info,
        "keywords_text": keywords_text
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
        temperature=llm_config.get("temperature", 0.3),
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
    
    return SemanticJudgeOutput(semantic_bad=result_text)
