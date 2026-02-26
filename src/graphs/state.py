"""
状态定义文件
亚马逊广告优化工作流（流量清洗 + 关键词收割）
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ==================== 合并工作流：亚马逊广告优化 ====================

class AdOptimizeInput(BaseModel):
    """亚马逊广告优化工作流的输入"""
    report_text: str = Field(..., description="用户粘贴的广告报表文本")
    product_info: str = Field(..., description="产品信息（标题+描述）")
    seed_keywords: str = Field(default="", description="种子关键词（可选，用于拓词）")


class AdOptimizeOutput(BaseModel):
    """亚马逊广告优化工作流的输出"""
    negative_keywords: List[Dict[str, Any]] = Field(default=[], description="否定关键词列表（止血）")
    recommend_keywords: List[Dict[str, Any]] = Field(default=[], description="新增关键词建议（拓词）")


# 汇聚节点：合并两个分支的结果
class MergeResultInput(BaseModel):
    """汇聚节点输入"""
    final_negative_list: List[Dict[str, Any]] = Field(default=[], description="否定关键词列表")
    keyword_recommend: List[Dict[str, Any]] = Field(default=[], description="关键词投放建议")


class MergeResultOutput(BaseModel):
    """汇聚节点输出"""
    negative_keywords: List[Dict[str, Any]] = Field(default=[], description="否定关键词列表（止血）")
    recommend_keywords: List[Dict[str, Any]] = Field(default=[], description="新增关键词建议（拓词）")


# ==================== 流量清洗分支节点状态 ====================

# 分发节点输入
class DispatchInput(BaseModel):
    """分发节点输入"""
    report_text: str = Field(default="", description="广告报表文本")
    product_info: str = Field(default="", description="产品信息")
    seed_keywords: str = Field(default="", description="种子关键词")


class DispatchOutput(BaseModel):
    """分发节点输出"""
    report_text: str = Field(default="", description="广告报表文本")
    product_info: str = Field(default="", description="产品信息")
    seed_keywords: str = Field(default="", description="种子关键词")

class KeywordData(BaseModel):
    """单个关键词数据"""
    search_term: str = Field(..., description="搜索词")
    clicks: int = Field(default=0, description="点击数")
    spend: float = Field(default=0.0, description="花费")
    orders: int = Field(default=0, description="订单数")


class BadKeyword(BaseModel):
    """否定关键词数据"""
    search_term: str = Field(..., description="搜索词")
    clicks: int = Field(default=0, description="点击数")
    spend: float = Field(default=0.0, description="花费")
    orders: int = Field(default=0, description="订单数")
    reason: str = Field(default="", description="否定原因")


# 工作流A的输入输出
class TrafficCleanInput(BaseModel):
    """工作流A的输入"""
    report_text: str = Field(..., description="用户粘贴的广告报表文本")
    product_info: str = Field(..., description="产品信息（标题+描述）")


class TrafficCleanOutput(BaseModel):
    """工作流A的输出"""
    final_negative_list: List[Dict[str, Any]] = Field(default=[], description="最终否定关键词列表")


# 节点A1：数据预处理
class DataPreprocessInput(BaseModel):
    """数据预处理节点输入"""
    report_text: str = Field(..., description="广告报表文本")


class DataPreprocessOutput(BaseModel):
    """数据预处理节点输出"""
    data: List[Dict[str, Any]] = Field(default=[], description="结构化关键词列表")


# 节点A2：统计规则筛选
class StatsFilterInput(BaseModel):
    """统计规则筛选节点输入"""
    data: List[Dict[str, Any]] = Field(default=[], description="结构化关键词列表")


class StatsFilterOutput(BaseModel):
    """统计规则筛选节点输出"""
    bad_keywords: List[Dict[str, Any]] = Field(default=[], description="统计否定词")
    remaining_keywords: List[Dict[str, Any]] = Field(default=[], description="剩余待判断的词")


# 节点A3：LLM语义相关性判断
class SemanticJudgeInput(BaseModel):
    """语义相关性判断节点输入"""
    remaining_keywords: List[Dict[str, Any]] = Field(default=[], description="剩余待判断的词")
    product_info: str = Field(..., description="产品信息")


class SemanticJudgeOutput(BaseModel):
    """语义相关性判断节点输出"""
    semantic_bad: str = Field(default="", description="语义不相关词（文本格式）")


# 节点A4：合并否定词
class MergeNegativesInput(BaseModel):
    """合并否定词节点输入"""
    bad_keywords: List[Dict[str, Any]] = Field(default=[], description="统计否定词")
    semantic_bad: str = Field(default="", description="语义不相关词")


class MergeNegativesOutput(BaseModel):
    """合并否定词节点输出"""
    final_negative_list: List[Dict[str, Any]] = Field(default=[], description="最终否定词列表")


# ==================== 工作流B：关键词收割 ====================

class KeywordRecommend(BaseModel):
    """关键词推荐数据"""
    keyword: str = Field(..., description="关键词")
    match_type: str = Field(default="", description="匹配类型")
    competition: str = Field(default="", description="竞争度")
    bid: str = Field(default="", description="出价建议")
    reason: str = Field(default="", description="建议原因")


# 工作流B的输入输出
class KeywordHarvestInput(BaseModel):
    """工作流B的输入"""
    product_description: str = Field(..., description="产品描述")
    seed_keywords: str = Field(..., description="种子关键词")


class KeywordHarvestOutput(BaseModel):
    """工作流B的输出"""
    keyword_recommend: List[Dict[str, Any]] = Field(default=[], description="关键词投放建议")


# 节点B1：LLM场景拓词
class ExpandKeywordsInput(BaseModel):
    """场景拓词节点输入"""
    product_info: str = Field(default="", description="产品信息（标题+描述）")
    seed_keywords: str = Field(default="", description="种子关键词")


class ExpandKeywordsOutput(BaseModel):
    """场景拓词节点输出"""
    longtail_keywords: str = Field(default="", description="长尾关键词列表")


# 节点B2：竞争度打分
class CompetitionScoreInput(BaseModel):
    """竞争度打分节点输入"""
    longtail_keywords: str = Field(default="", description="长尾关键词列表")


class CompetitionScoreOutput(BaseModel):
    """竞争度打分节点输出"""
    keyword_recommend: List[Dict[str, Any]] = Field(default=[], description="关键词投放建议")
