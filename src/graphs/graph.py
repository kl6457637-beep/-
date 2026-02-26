"""
亚马逊广告优化工作流
从"止血"和"拓词"两个方面同时优化广告

并行执行两个分支：
- 分支1：流量清洗（止血）- 找出需要否定的垃圾词
- 分支2：关键词收割（拓词）- 生成新增关键词建议

最后汇聚两个分支的结果
"""
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

# 导入状态定义
from graphs.state import (
    AdOptimizeInput,
    AdOptimizeOutput,
    DispatchInput,
    DispatchOutput,
    DataPreprocessInput,
    DataPreprocessOutput,
    StatsFilterInput,
    StatsFilterOutput,
    SemanticJudgeInput,
    SemanticJudgeOutput,
    MergeNegativesInput,
    MergeNegativesOutput,
    ExpandKeywordsInput,
    ExpandKeywordsOutput,
    CompetitionScoreInput,
    CompetitionScoreOutput,
    MergeResultInput,
    MergeResultOutput
)

# 导入节点函数
from graphs.nodes.dispatch_node import dispatch_node
from graphs.nodes.data_preprocess_node import data_preprocess_node
from graphs.nodes.stats_filter_node import stats_filter_node
from graphs.nodes.semantic_judge_node import semantic_judge_node
from graphs.nodes.merge_negatives_node import merge_negatives_node
from graphs.nodes.expand_keywords_node import expand_keywords_node
from graphs.nodes.competition_score_node import competition_score_node
from graphs.nodes.merge_result_node import merge_result_node


# 定义全局状态
class AdOptimizeGlobalState(BaseModel):
    """亚马逊广告优化工作流的全局状态"""
    # 输入
    report_text: str = Field(default="", description="广告报表文本")
    product_info: str = Field(default="", description="产品信息")
    seed_keywords: str = Field(default="", description="种子关键词")
    
    # 流量清洗分支中间状态
    data: List[Dict[str, Any]] = Field(default=[], description="结构化关键词列表")
    bad_keywords: List[Dict[str, Any]] = Field(default=[], description="统计否定词")
    remaining_keywords: List[Dict[str, Any]] = Field(default=[], description="剩余待判断的词")
    semantic_bad: str = Field(default="", description="语义不相关词")
    final_negative_list: List[Dict[str, Any]] = Field(default=[], description="最终否定词列表")
    
    # 关键词收割分支中间状态
    longtail_keywords: str = Field(default="", description="长尾关键词列表")
    keyword_recommend: List[Dict[str, Any]] = Field(default=[], description="关键词投放建议")
    
    # 最终输出
    negative_keywords: List[Dict[str, Any]] = Field(default=[], description="否定关键词列表（止血）")
    recommend_keywords: List[Dict[str, Any]] = Field(default=[], description="新增关键词建议（拓词）")


def create_ad_optimize_graph() -> StateGraph:
    """
    创建亚马逊广告优化工作流图
    """
    # 创建状态图，指定输入输出
    builder = StateGraph(
        AdOptimizeGlobalState,
        input_schema=AdOptimizeInput,
        output_schema=AdOptimizeOutput
    )
    
    # ==================== 分发节点 ====================
    builder.add_node("dispatch", dispatch_node)
    
    # ==================== 流量清洗分支节点 ====================
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
    
    # ==================== 关键词收割分支节点 ====================
    builder.add_node(
        "expand_keywords",
        expand_keywords_node,
        metadata={
            "type": "agent",
            "llm_cfg": "config/expand_keywords_llm_cfg.json"
        }
    )
    builder.add_node("competition_score", competition_score_node)
    
    # ==================== 汇聚节点 ====================
    builder.add_node("merge_result", merge_result_node)
    
    # ==================== 设置入口点 ====================
    builder.set_entry_point("dispatch")
    
    # ==================== 从分发节点触发两个并行分支 ====================
    builder.add_edge("dispatch", "data_preprocess")
    builder.add_edge("dispatch", "expand_keywords")
    
    # ==================== 流量清洗分支链路 ====================
    builder.add_edge("data_preprocess", "stats_filter")
    builder.add_edge("stats_filter", "semantic_judge")
    builder.add_edge("semantic_judge", "merge_negatives")
    
    # ==================== 关键词收割分支链路 ====================
    builder.add_edge("expand_keywords", "competition_score")
    
    # ==================== 汇聚两个分支 ====================
    # merge_negatives 和 competition_score 都完成后，执行 merge_result
    builder.add_edge(["merge_negatives", "competition_score"], "merge_result")
    
    # ==================== 结束 ====================
    builder.add_edge("merge_result", END)
    
    return builder


# 编译图
ad_optimize_graph_builder = create_ad_optimize_graph()
main_graph = ad_optimize_graph_builder.compile()

__all__ = ["main_graph", "ad_optimize_graph_builder"]
