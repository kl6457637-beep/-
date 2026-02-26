## 项目概述
- **名称**: 亚马逊广告优化工作流
- **功能**: 亚马逊广告优化工作流通过并行分支同时处理流量清洗（止血）和关键词收割（拓词）任务

### 节点清单
| 节点名 | 文件位置 | 类型 | 功能描述 | 分支逻辑 | 配置文件 |
|-------|---------|------|-------------------------|---------|---------|
| dispatch | `nodes/dispatch_node.py` | task | 分发节点，初始化并行分支的输入数据 | → data_preprocess, expand_keywords | - |
| data_preprocess | `nodes/data_preprocess_node.py` | task | 数据预处理，解析广告报表文本 | → stats_filter | - |
| stats_filter | `nodes/stats_filter_node.py` | task | 统计规则筛选，识别高点击无转化的词 | → semantic_judge | - |
| semantic_judge | `nodes/semantic_judge_node.py` | agent | LLM语义相关性判断，识别语义不相关的词 | → merge_negatives | `config/semantic_judge_llm_cfg.json` |
| merge_negatives | `nodes/merge_negatives_node.py` | task | 合并否定词，整合统计否定词和语义否定词 | → merge_result | - |
| expand_keywords | `nodes/expand_keywords_node.py` | agent | 场景化长尾拓词，基于产品信息生成场景化关键词 | → competition_score | `config/expand_keywords_llm_cfg.json` |
| competition_score | `nodes/competition_score_node.py` | task | 关键词竞争度分级，评估竞争度和出价建议 | → merge_result | - |
| merge_result | `nodes/merge_result_node.py` | task | 汇聚节点，合并两个分支的输出 | → END | - |

**类型说明**: task(task节点) / agent(大模型) / condition(条件分支) / looparray(列表循环) / loopcond(条件循环)

## 工作流架构

```
                    ┌──────────────────────────────────────┐
                    │           GraphInput                 │
                    │  report_text, product_info,          │
                    │  seed_keywords                       │
                    └──────────────────┬───────────────────┘
                                       │
                                       ▼
                              ┌────────────────┐
                              │    dispatch    │
                              └───────┬────────┘
                    ┌─────────────────┴─────────────────┐
                    │                                   │
                    ▼                                   ▼
    ┌───────────────────────────────┐   ┌───────────────────────────────┐
    │      流量清洗分支（止血）       │   │      关键词收割分支（拓词）     │
    │                               │   │                               │
    │  data_preprocess              │   │  expand_keywords              │
    │        ↓                      │   │        ↓                      │
    │  stats_filter                 │   │  competition_score            │
    │        ↓                      │   │                               │
    │  semantic_judge               │   │                               │
    │        ↓                      │   │                               │
    │  merge_negatives              │   │                               │
    └───────────────┬───────────────┘   └───────────────┬───────────────┘
                    │                                   │
                    └─────────────────┬─────────────────┘
                                      │
                                      ▼
                             ┌────────────────┐
                             │  merge_result  │
                             └───────┬────────┘
                                     │
                                     ▼
                    ┌──────────────────────────────────────┐
                    │          GraphOutput                 │
                    │  negative_keywords (止血)            │
                    │  recommend_keywords (拓词)           │
                    └──────────────────────────────────────┘
```

## 技能使用
- 节点 `semantic_judge` 使用 LLM 大语言模型技能
- 节点 `expand_keywords` 使用 LLM 大语言模型技能

## 输入输出

### 输入 (AdOptimizeInput)
| 字段 | 类型 | 必填 | 描述 |
|-----|------|-----|------|
| report_text | str | 是 | 用户粘贴的广告报表文本 |
| product_info | str | 是 | 产品信息（标题+描述） |
| seed_keywords | str | 否 | 种子关键词（可选，用于拓词） |

### 输出 (AdOptimizeOutput)
| 字段 | 类型 | 描述 |
|-----|------|------|
| negative_keywords | List[Dict] | 否定关键词列表（止血），包含 search_term, clicks, spend, orders, reason |
| recommend_keywords | List[Dict] | 新增关键词建议（拓词），包含 keyword, match_type, competition, bid, reason |

## 文件结构
```
src/
├── graphs/
│   ├── state.py              # 状态定义（全局状态、节点出入参）
│   ├── graph.py              # 主图编排
│   ├── nodes/
│   │   ├── dispatch_node.py           # 分发节点
│   │   ├── data_preprocess_node.py    # 数据预处理
│   │   ├── stats_filter_node.py       # 统计规则筛选
│   │   ├── semantic_judge_node.py     # LLM语义判断
│   │   ├── merge_negatives_node.py    # 合并否定词
│   │   ├── expand_keywords_node.py    # 场景拓词
│   │   ├── competition_score_node.py  # 竞争度打分
│   │   └── merge_result_node.py       # 结果汇聚
│   ├── traffic_clean_graph.py         # 独立流量清洗工作流
│   └── keyword_harvest_graph.py       # 独立关键词收割工作流
├── config/
│   ├── semantic_judge_llm_cfg.json    # 语义判断LLM配置
│   └── expand_keywords_llm_cfg.json   # 拓词LLM配置
└── main.py                            # 服务入口
```

## 使用示例

### 输入示例
```json
{
    "report_text": "wireless mouse 50 25.5 3\nbluetooth mouse 30 15.2 2\ngaming keyboard 15 8.0 0\ncoffee maker 20 10.0 0",
    "product_info": "无线蓝牙鼠标，适合办公和游戏，支持多设备连接，静音点击",
    "seed_keywords": "wireless mouse, bluetooth mouse"
}
```

### 输出示例
```json
{
    "negative_keywords": [
        {"search_term": "gaming keyboard", "clicks": 15, "spend": 8.0, "orders": 0, "reason": "高点击无转化"},
        {"search_term": "coffee maker", "clicks": 20, "spend": 10.0, "orders": 0, "reason": "语义不相关"}
    ],
    "recommend_keywords": [
        {"keyword": "silent wireless mouse for office", "match_type": "Exact", "competition": "低竞争·蓝海", "bid": "高", "reason": "长词+场景精准，转化高"}
    ]
}
```
