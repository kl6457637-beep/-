"""
统计规则筛选节点
硬规则判断亏损词：高点击零单、高花费零单
"""
from typing import List, Dict, Any
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import StatsFilterInput, StatsFilterOutput


def stats_filter_node(
    state: StatsFilterInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> StatsFilterOutput:
    """
    title: 统计规则筛选
    desc: 根据硬规则判断亏损词，识别高点击无转化和高花费无转化的关键词
    """
    data: List[Dict[str, Any]] = state.data
    avg_price = 20.0  # 平均价格，可用于调整阈值
    
    bad_keywords: List[Dict[str, Any]] = []
    normal_keywords: List[Dict[str, Any]] = []
    
    for row in data:
        st = str(row.get("search_term", ""))
        cli = int(row.get("clicks", 0))
        spe = float(row.get("spend", 0.0))
        ords = int(row.get("orders", 0))
        
        reason = None
        if ords == 0:
            if cli > 10:
                reason = "高点击无转化"
            elif spe > avg_price / 2:
                reason = "高花费无转化"
        
        if reason:
            bad_keywords.append({
                "search_term": st,
                "clicks": cli,
                "spend": spe,
                "orders": ords,
                "reason": reason
            })
        else:
            normal_keywords.append({
                "search_term": st,
                "clicks": cli,
                "spend": spe,
                "orders": ords
            })
    
    return StatsFilterOutput(
        bad_keywords=bad_keywords,
        remaining_keywords=normal_keywords
    )
