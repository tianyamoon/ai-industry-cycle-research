# AI终端_具身智能整机BOM与订阅ARPU对照总表
> 所属模块：03_结果层/01_总表整合与AI映射
> 生成日期：2026-07-04
> 研究定位：把终端 / 具身智能这条线从 `钱包待补表中的一段` 升级成结果层独立入口，集中回答三个问题：`当前第一笔钱包先花在哪里`、`厚利润池更可能落在哪`、`订阅 ARPU 目前能否压过整机硬件`。
> 使用边界：本表不伪造精确 BOM 百分比，不把主题热度当成产业兑现；截至 `2026-07-04`，本表能正式上收的是 `整机价格锚 + 第一批拆机 / 芯片识别锚 + 消费级订阅 ARPU 锚`，还不能写成跨品类统一精确 BOM。
> 来源说明：本表优先采用官方售价页、官方订阅页、官方帮助页和 iFixit 拆机 / 芯片识别页；动态页面如地区价格可能随区域与版本变化，因此统一以当前公开美元口径为主。

---

## 一句话结论

截至 `2026-07-04`，终端 / 具身智能最稳的正式判断已经不是“未来可能从硬件转订阅”，而是：`当前第一笔大钱包仍显著先落在整机硬件，端侧 SoC / 内存 / 感知器件更接近厚利润池，消费级订阅 ARPU 仍主要是后装增量钱包。`

---

## 一、当前可正式采用的固定口径

本表固定使用以下字段：

`整机或部件官方价格 / 当前订阅价格 / 年化订阅 ARPU / 硬件价格折算订阅年数 / 当前已知芯片或 BOM 锚 / 当前总钱包判断 / 当前利润池判断 / 当前边界`

使用纪律：

1. 不把拆机里识别到的芯片，直接写成精确 BOM 占比。
2. 不把“免费 AI 功能”直接等同于没有订阅钱包，而是看它是否保留后续收费可能。
3. 不把眼镜、手机、机器狗、双足机器人混写成同一条量产曲线。
4. 订阅 ARPU 统一年化，再与整机一次性价格做对照，避免只看月费造成误判。

---

## 二、整机价格与订阅 ARPU 对照总表

| 类别 | 样本 | 当前官方价格 | 当前订阅口径 | 年化 ARPU | 硬件价格折算订阅年数 | 当前已知芯片 / BOM 锚 | 当前总钱包判断 | 当前利润池判断 | 当前边界 |
|---|---|---:|---|---:|---:|---|---|---|---|
| AI 订阅基准 | ChatGPT Plus | `$20 / 月` | 官方消费级标准订阅 | `$240 / 年` | `1.00x` | 不适用 | 消费级后装增量钱包基准 | 平台入口与服务订阅 | 不是终端硬件 BOM |
| AI 订阅基准 | Google AI Pro | `$19.99 / 月` | 官方消费级标准订阅 | `$239.88 / 年` | `1.00x` | 不适用 | 消费级后装增量钱包基准 | 平台入口与服务订阅 | 地区权益可能变化 |
| AI 订阅高阶基准 | Google AI Ultra | `$99.99 / 月` | 官方高阶订阅 | `$1,199.88 / 年` | `5.00x` ChatGPT Plus | 不适用 | 高阶用户增量钱包 | 平台入口、模型与增值权益 | 不适合直接代表大众消费级 ARPU |
| AI 眼镜 | Meta Glasses | `$299` 起 | Meta One Premium 为可选增值订阅 | 待核 | `1.25 年` ChatGPT Plus | iFixit 已识别 `Qualcomm AR1 Gen 1 + 32GB flash memory` | 第一笔钱包先落整机 | 端侧 SoC、存储和光学模组更接近利润池 | 订阅价格口径仍未形成稳定公开美元锚 |
| AI 手机 | Galaxy S25 | `$799.99` | Galaxy AI 基础功能当前免费，后续增强功能可能收费 | `0` 或待后续收费 | `3.33 年` ChatGPT Plus；`3.34 年` Google AI Pro | 官方写明 `Snapdragon 8 Elite for Galaxy`；Samsung 与 iFixit 已给出端侧芯片和内存锚 | 当前总钱包显著先落整机 | 端侧 SoC / 内存更接近厚利润池 | 仍缺统一拆机 BOM 占比 |
| 机器狗 | Unitree Go2 | `$1,600` 起 | 当前不以消费级订阅为主 | 待核 | `6.67 年` ChatGPT Plus | 官方公开 `4D LiDAR L2`、约 `15kg` 机身、`3000W` 峰值功率等 | 当前总钱包先落本体 | 传感器 / LiDAR / 控制器件为潜在利润池 | 不是标准消费电子 ARPU 逻辑 |
| 双足机器人 | Unitree R1 | `$4,900` 起 | 当前不以消费级订阅为主 | 待核 | `20.42 年` ChatGPT Plus | 官方已给出整机价格与多版本定位 | 当前总钱包远高于订阅钱包 | 关节、电驱、感知与控制器件更可能吃利润池 | 量产和交付节奏仍待验证 |
| 双足机器人 | Unitree G1 | `$13.5K` 起 | 当前不以消费级订阅为主 | 待核 | `56.25 年` ChatGPT Plus | 官方已给出整机价格、关节空间和 OTA 口径 | 当前是典型重硬件钱包 | 核心控制、执行与感知器件更接近利润池 | 仍缺连续拆机与部件成本分层 |
| 感知器件 | Unitree 4D LiDAR L2 | `$419` | 不适用 | 不适用 | 约为 `0.52 部` Galaxy S25；约为 `0.26 台` Go2 | 官方公开 `360°×96°`、`30m`、`230g`、`$419` | 是机器人 BOM 中可单独标价的重要部件 | 传感器 / 模组链利润池锚点之一 | 单部件价格不能替代整机 BOM 排序 |

---

## 三、当前已被正式锁定的事实

### 1. 硬件第一笔钱包显著大于主流消费级订阅 ARPU

当前公开美元口径下：

1. `ChatGPT Plus` 年化约 `$240`；
2. `Google AI Pro` 年化约 `$239.88`；
3. `Galaxy S25` 一次性价格约等于 `3.3 年` 主流消费级 AI 订阅；
4. `Unitree Go2 / R1 / G1` 分别约等于 `6.7 / 20.4 / 56.3 年` ChatGPT Plus。

这说明当前终端与具身智能的总钱包结构，短期内仍然明显偏向：

`硬件前装大钱包 > 订阅后装增量钱包`

### 2. 端侧 SoC 与关键感知器件已经有第一批硬锚点

当前至少已经锁定三类硬锚：

1. `Meta Glasses` 的 iFixit 拆机已识别 `Qualcomm AR1 Gen 1 + 32GB flash memory`；
2. `Galaxy S25` 官方强调 `Snapdragon 8 Elite for Galaxy`，iFixit 已识别 `Snapdragon 8 Elite + 12GB LPDDR5X`；
3. `Unitree 4D LiDAR L2` 已能被官方单独标价到 `$419`。

这说明终端 / 具身智能链里，厚利润池更可能先沉到：

`端侧 SoC / 内存 / 关键感知器件`

而不是均匀分散在全部整机部件里。

### 3. 免费 AI 功能并不等于订阅钱包不存在

当前口径要分开看：

1. `Galaxy AI` 基础功能当前免费，但三星官方明确保留未来增强功能或新服务收费的可能；
2. `Meta One Premium` 已经说明 AI 眼镜存在增值订阅方向；
3. `ChatGPT Plus / Google AI Pro / Ultra` 已提供明确消费级订阅价格锚。

因此更准确的判断是：

`订阅钱包已经存在，但在多数终端形态里仍未压过第一笔整机钱包。`

---

## 四、当前可正式上收的结论

1. 终端 / 具身智能当前最稳的总钱包中心，仍然是 `整机硬件`，不是订阅。
2. 端侧 SoC、内存和关键感知器件，已经比“泛终端硬件”更接近利润池口径，因为它们既被官方营销单独强调，也已被拆机识别。
3. 消费级 AI 订阅当前已经形成清晰 ARPU 锚，但更像 `后装增量钱包`，而不是短期内取代整机售价的主钱包。
4. 机器人链与手机 / 眼镜链不能混写：前者当前更像 `重硬件 + 感知器件单独定价`，后者更像 `整机 + 端侧 SoC + 后续订阅增量`。

---

## 五、当前仍未闭环的点

1. `AI 手机 / AI 眼镜 / 机器人` 之间仍缺统一、连续、可复核的精确 BOM 百分比。
2. `Meta One Premium` 当前缺稳定、统一的公开美元价格锚，因此本表只把它视作“订阅方向存在”，不写进年化 ARPU。
3. `Galaxy AI` 当前更多是免费基础能力 + 未来可能收费的状态，因此还不能把三星端侧 AI 写成成熟订阅模型。
4. 机器人链仍缺连续出货量、持续服务 ARPU 与量产后部件降本路径。

---

## 六、对钱包主研究的意义

本表补上的不是新的题材叙事，而是把终端 / 具身智能从“方向已经明确但仍停留在待补表”推进到：

1. 已有 `整机价格锚`；
2. 已有 `订阅年化 ARPU 锚`；
3. 已有 `端侧芯片 / 感知器件` 第一批 BOM 锚；
4. 已能正式回答“当前总钱包先落硬件，订阅仍属后装增量”。

因此，这一层现在可以正式从“待补口径”升级到“结果层可引用但仍保留边界”的状态。

---

## 七、本版来源入口

1. [Meta Store](https://www.meta.com/)
2. [Meta One subscription for AI glasses](https://www.meta.com/help/ai-glasses/1384571770097740/)
3. [Samsung Galaxy S25 官方购买页](https://www.samsung.com/us/smartphones/galaxy-s25/buy/galaxy-s25-128gb-unlocked-sku-sm-s931udbaxaa/)
4. [Galaxy S25 官方介绍页](https://www.samsung.com/us/smartphones/galaxy-s25/)
5. [Galaxy AI 官方页](https://www.samsung.com/us/galaxy-ai/)
6. [Samsung Galaxy S25 Ultra Chip ID - iFixit](https://www.ifixit.com/Guide/Samsung%2BGalaxy%2BS25%2BUltra%2BChip%2BID/181690)
7. [Oakley x Meta HSTN Smartglasses Teardown - iFixit](https://www.ifixit.com/News/112649/oakley-x-meta-hstn-smartglasses-teardown-cool-shades-tough-fix)
8. [Unitree G1](https://www.unitree.com/g1/)
9. [Unitree R1](https://www.unitree.com/R1/)
10. [Unitree Go2](https://www.unitree.com/go2/)
11. [Unitree 4D LiDAR L2](https://www.unitree.com/mobile/L2/)
12. [ChatGPT Pricing](https://chatgpt.com/pricing/)
13. [Google AI Pro / Ultra](https://gemini.google/subscriptions/)
