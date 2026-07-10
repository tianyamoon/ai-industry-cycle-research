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
