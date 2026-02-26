"""
数据预处理节点
将用户粘贴的报表文本转换为结构化JSON
"""
from typing import List, Dict, Any
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import DataPreprocessInput, DataPreprocessOutput


def data_preprocess_node(
    state: DataPreprocessInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> DataPreprocessOutput:
    """
    title: 数据预处理
    desc: 将用户粘贴的广告报表文本解析为结构化的关键词列表，提取搜索词、点击数、花费、订单数等信息
    """
    # 获取输入文本
    text = state.report_text
    lines: List[str] = text.strip().split("\n")
    data: List[Dict[str, Any]] = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        parts = line.split()
        if len(parts) >= 4:
            # 假设格式: 搜索词 点击数 花费 订单数
            search_term = " ".join(parts[:-3])
            try:
                clicks = int(parts[-3])
                spend = float(parts[-2])
                orders = int(parts[-1])
                
                data.append({
                    "search_term": search_term,
                    "clicks": clicks,
                    "spend": spend,
                    "orders": orders
                })
            except (ValueError, IndexError):
                # 跳过无法解析的行
                continue
    
    return DataPreprocessOutput(data=data)
