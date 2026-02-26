"""
合并否定词节点
合并统计否定词和语义否定词
"""
from typing import List, Dict, Any
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import MergeNegativesInput, MergeNegativesOutput


def merge_negatives_node(
    state: MergeNegativesInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> MergeNegativesOutput:
    """
    title: 合并否定词
    desc: 将统计规则筛选出的否定词与语义判断出的不相关词合并，生成最终的否定关键词列表
    """
    bad_keywords: List[Dict[str, Any]] = state.bad_keywords
    semantic_bad: str = state.semantic_bad
    
    # 解析语义否定词
    semantic_list: List[Dict[str, Any]] = []
    
    if semantic_bad:
        semantic_lines = semantic_bad.strip().split("\n")
        for line in semantic_lines:
            line = line.strip()
            if not line:
                continue
            
            if "|" in line:
                parts = line.split("|")
                st = parts[0].strip()
                reason = parts[1].strip() if len(parts) > 1 else "语义不相关"
                semantic_list.append({
                    "search_term": st,
                    "clicks": 0,
                    "spend": 0.0,
                    "orders": 0,
                    "reason": reason
                })
            elif line:
                # 如果没有分隔符，整行作为搜索词
                semantic_list.append({
                    "search_term": line,
                    "clicks": 0,
                    "spend": 0.0,
                    "orders": 0,
                    "reason": "语义不相关"
                })
    
    # 合并两个列表
    final_list = bad_keywords + semantic_list
    
    return MergeNegativesOutput(final_negative_list=final_list)
