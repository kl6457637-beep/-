"""
汇聚节点
合并流量清洗和关键词收割两个分支的结果
"""
from typing import List, Dict, Any
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import MergeResultInput, MergeResultOutput


def merge_result_node(
    state: MergeResultInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> MergeResultOutput:
    """
    title: 结果汇聚
    desc: 合并流量清洗分支的否定关键词和关键词收割分支的新增关键词建议，输出最终的广告优化方案
    """
    # 获取两个分支的结果
    final_negative_list: List[Dict[str, Any]] = state.final_negative_list
    keyword_recommend: List[Dict[str, Any]] = state.keyword_recommend
    
    # 返回合并后的结果
    return MergeResultOutput(
        negative_keywords=final_negative_list,
        recommend_keywords=keyword_recommend
    )
