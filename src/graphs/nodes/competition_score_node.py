"""
竞争度打分节点
为关键词打分并给出投放建议
"""
from typing import List, Dict, Any
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import CompetitionScoreInput, CompetitionScoreOutput


def competition_score_node(
    state: CompetitionScoreInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> CompetitionScoreOutput:
    """
    title: 关键词竞争度分级
    desc: 根据关键词长度和特征判断竞争度，给出匹配类型、出价建议等投放策略
    """
    text: str = state.longtail_keywords
    lines: List[str] = text.strip().split("\n")
    
    res: List[Dict[str, Any]] = []
    
    for line in lines:
        kw = line.strip()
        if not kw:
            continue
        
        # 移除可能的序号前缀
        if kw[0].isdigit():
            kw = kw.split(".", 1)[-1].strip()
            kw = kw.split(")", 1)[-1].strip()
        
        if not kw:
            continue
        
        words = kw.split()
        cnt = len(words)
        
        typ = "Exact"
        level = "中等"
        bid = "中"
        reason = ""
        
        if cnt >= 3 and ("for" in kw.lower() or "with" in kw.lower()):
            level = "低竞争·蓝海"
            typ = "Exact"
            bid = "高"
            reason = "长词+场景精准，转化高"
        elif cnt <= 2:
            level = "高竞争·红海"
            typ = "Broad"
            bid = "低"
            reason = "大词，竞争激烈"
        else:
            level = "中等竞争"
            typ = "Phrase"
            bid = "中"
            reason = "可测试"
        
        res.append({
            "keyword": kw,
            "match_type": typ,
            "competition": level,
            "bid": bid,
            "reason": reason
        })
    
    return CompetitionScoreOutput(keyword_recommend=res)
