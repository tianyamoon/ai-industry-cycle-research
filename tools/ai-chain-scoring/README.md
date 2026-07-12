# AI Chain Scoring Tools

本目录保存 AI 产业链周评分可公开、可复现的机器闸门和 Luna HTTP 客户端。技能编排不放在仓库内，由股票项目共享技能维护。

## 根目录配置

统一使用以下优先级：

1. 命令行参数
2. 环境变量
3. 从当前目录或脚本位置向上查找仓库标记

环境变量：

- `AI_INDUSTRY_RESEARCH_ROOT`
- `TRADE_SYSTEM_ROOT`
- `LUNA_STOCK_MCP_URL`

没有明确配置时，工具不会回退到个人机器路径或私网地址。

## 全产业链百亿观察池

`large_cap_observation_pool.py` 先从已有 AI 候选中生成强制观察池，再从全 A 市值清单反查所有百亿标的。全市场中尚未进入 AI 候选宇宙的标的会保留为“待路由审计”，不会被直接认定为 AI，也不会静默遗漏。

```powershell
python tools/ai-chain-scoring/large_cap_observation_pool.py --repo-root . --input <候选CSV> --output <观察池CSV> --summary <观察池摘要JSON> --market-audit-output <全市场审计CSV> --market-audit-summary <全市场审计摘要JSON> --as-of-date YYYY-MM-DD
```

规则：总市值不低于 `100亿元` 的已路由 AI 标的为强制观察；`90-100亿元` 保留边界复核。脚本在全市场市值降到边界以下前持续翻页，若显式设置分页上限而未达到边界会报错，不会输出不完整的“全市场”结果。

## 百亿待路由实填

`large_cap_routing.py` 读取全市场市值路由审计 CSV，使用公司资料中的主营业务与机构类型完成三类预筛：`AI产业链相关 / 非AI / 信息不足`。它不读取概念热度或新闻标题；泛材料、通用制造、电力与基础设施没有直接产品依据时保留为“信息不足”。公司资料属于 `B` 级预筛，只用于 `L0` 防漏和观察池扩容，不用于经营验证、评分或结果层结论。

可选的 `--observation-output` 与 `--observation-summary` 会把既有 AI 候选和本批“AI产业链相关”标的合并为当前观察池。`--profile-cache` 可复用上一轮分流 CSV 的主营业务快照，避免重复访问来源站。

```powershell
python tools/ai-chain-scoring/large_cap_routing.py --repo-root . --input <全市场审计CSV> --output <路由实填CSV> --summary <路由实填摘要JSON> --observation-output <当前观察池CSV> --observation-summary <当前观察池摘要JSON> --as-of-date YYYY-MM-DD
```

## 周评分闸门

```powershell
python tools/ai-chain-scoring/check_weekly_completion.py --mode stage --coverage scoped --week YYYY-MM-DD --report <报告.md> --manifest <完成清单.csv> --wiki-root <wiki根目录>
```

正式周更把 `--mode` 改为 `formal`，全量覆盖把 `--coverage` 改为 `full`。

完成清单必须显式记录 Wiki 承接状态：

- `wiki_sync_status`：仅允许 `已同步`、`无需同步`、`待同步`。
- `wiki_skip_reason`：`无需同步` 或 `待同步` 时必填。
- `已同步`：checker 会校验 canonical Wiki 页面、对应周次评分和评分历史。
- `formal`：不允许保留 `待同步`；没有合格 canonical 页时应写 `无需同步` 及原因，不批量生成低质量页面。

## Luna HTTP 客户端

调用前先列出工具及参数 schema：

```powershell
python tools/ai-chain-scoring/luna_http_client.py list-tools
```

随后通过 `call`、`audit-tech` 或 `validate` 子命令调用。结果优先读取 `structuredContent`，并审查 `meta.actual_source`、`fallback_used`、`confidence` 和 `warnings`。

## 测试

```powershell
python -m pytest tools/ai-chain-scoring/tests -q
```
