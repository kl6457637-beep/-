"""
工作流B：关键词收割（拓词+竞争分级）
输入产品信息 → 生成长尾词 → 自动打分 → 给出投放建议
"""
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import (
    KeywordHarvestInput,
    KeywordHarvestOutput,
    ExpandKeywordsInput,
    ExpandKeywordsOutput,
    CompetitionScoreInput,
    CompetitionScoreOutput
)

from graphs.nodes.expand_keywords_node import expand_keywords_node
from graphs.nodes.competition_score_node import competition_score_node


# 定义工作流B的全局状态
class KeywordHarvestGlobalState(BaseModel):
    """工作流B的全局状态"""
    product_description: str = Field(default="", description="产品描述")
    seed_keywords: str = Field(default="", description="种子关键词")
    longtail_keywords: str = Field(default="", description="长尾关键词列表")
    keyword_recommend: List[Dict[str, Any]] = Field(default=[], description="关键词投放建议")


def create_keyword_harvest_graph() -> StateGraph:
    """
    创建关键词收割工作流图
    """
    # 创建状态图，指定输入输出
    builder = StateGraph(
        KeywordHarvestGlobalState,
        input_schema=KeywordHarvestInput,
        output_schema=KeywordHarvestOutput
    )
    
    # 添加节点
    builder.add_node(
        "expand_keywords",
        expand_keywords_node,
        metadata={
            "type": "agent",
            "llm_cfg": "config/expand_keywords_llm_cfg.json"
        }
    )
    builder.add_node("competition_score", competition_score_node)
    
    # 设置入口点
    builder.set_entry_point("expand_keywords")
    
    # 添加边
    builder.add_edge("expand_keywords", "competition_score")
    builder.add_edge("competition_score", END)
    
    return builder


# 编译图
keyword_harvest_graph_builder = create_keyword_harvest_graph()
keyword_harvest_graph = keyword_harvest_graph_builder.compile()
