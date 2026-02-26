"""
工作流A：流量清洗（止血）
上传广告搜索词报告 → 自动找出必须精准否定的垃圾词
"""
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state import (
    TrafficCleanInput,
    TrafficCleanOutput,
    DataPreprocessInput,
    DataPreprocessOutput,
    StatsFilterInput,
    StatsFilterOutput,
    SemanticJudgeInput,
    SemanticJudgeOutput,
    MergeNegativesInput,
    MergeNegativesOutput
)

from graphs.nodes.data_preprocess_node import data_preprocess_node
from graphs.nodes.stats_filter_node import stats_filter_node
from graphs.nodes.semantic_judge_node import semantic_judge_node
from graphs.nodes.merge_negatives_node import merge_negatives_node


# 定义工作流A的全局状态
class TrafficCleanGlobalState(BaseModel):
    """工作流A的全局状态"""
    report_text: str = Field(default="", description="广告报表文本")
    product_info: str = Field(default="", description="产品信息")
    data: List[Dict[str, Any]] = Field(default=[], description="结构化关键词列表")
    bad_keywords: List[Dict[str, Any]] = Field(default=[], description="统计否定词")
    remaining_keywords: List[Dict[str, Any]] = Field(default=[], description="剩余待判断的词")
    semantic_bad: str = Field(default="", description="语义不相关词")
    final_negative_list: List[Dict[str, Any]] = Field(default=[], description="最终否定词列表")


def create_traffic_clean_graph() -> StateGraph:
    """
    创建流量清洗工作流图
    """
    # 创建状态图，指定输入输出
    builder = StateGraph(
        TrafficCleanGlobalState,
        input_schema=TrafficCleanInput,
        output_schema=TrafficCleanOutput
    )
    
    # 添加节点
    builder.add_node("data_preprocess", data_preprocess_node)
    builder.add_node("stats_filter", stats_filter_node)
    builder.add_node(
        "semantic_judge",
        semantic_judge_node,
        metadata={
            "type": "agent",
            "llm_cfg": "config/semantic_judge_llm_cfg.json"
        }
    )
    builder.add_node("merge_negatives", merge_negatives_node)
    
    # 设置入口点
    builder.set_entry_point("data_preprocess")
    
    # 添加边
    builder.add_edge("data_preprocess", "stats_filter")
    builder.add_edge("stats_filter", "semantic_judge")
    builder.add_edge("semantic_judge", "merge_negatives")
    builder.add_edge("merge_negatives", END)
    
    return builder


# 编译图
traffic_clean_graph_builder = create_traffic_clean_graph()
traffic_clean_graph = traffic_clean_graph_builder.compile()
