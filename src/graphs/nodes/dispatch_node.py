"""
分发节点
初始化并行分支的输入数据
"""
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context
from graphs.state import DispatchInput, DispatchOutput


def dispatch_node(
    state: DispatchInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> DispatchOutput:
    """
    title: 分发节点
    desc: 初始化并行分支的输入数据，确保两个分支都能正确接收到所需参数
    """
    return DispatchOutput(
        report_text=state.report_text,
        product_info=state.product_info,
        seed_keywords=state.seed_keywords
    )
