# AI全球芯片制造产业链与技术路线深度分析_第一版
> 所属模块：03_结果层/01_总表整合与AI映射  
> 生成日期：`2026-07-04`  
> 研究定位：把全球 AI 芯片制造、材料、存储配套和技术路线之争压成一份结果层深度分析，补足当前“全球样本有了、但制造深链还不够”的缺口。  
> 使用边界：本文优先使用官方年报、官方财报资料和公司官方技术页面；对路线之争部分，统一区分 `已验证主线`、`正在验证路线` 和 `观察层路线`。  

---

## 一句话结论

当前全球 AI 产业链最容易被低估的，不是 GPU 龙头本身，而是 `日本光刻与掩模材料簇 + 韩国 HBM 与先进封装配套簇 + InP 光器件衬底簇 + ABF / 玻璃基板路线簇 + CPO / HBM4 / MOR 等技术路线之争` 五条深链；如果这一层不补全，全球映射就会停留在“谁涨得最好”，而不是“谁真正控制了良率、功耗、互连密度和下一代封装路径”，更无法把海外制造瓶颈有效回落到 A 股承接位。

---

## 一、为什么这一层必须单独拆出来

此前全球样本层解决了：

1. 谁定义 AI 主链利润池。
2. 谁在云和平台层先兑现。
3. 机器人和 AI 玩具还处在哪个阶段。

但还没有充分回答：

1. AI 芯片制造为什么不是 `代工 + GPU` 两个词就能概括。
2. 日本材料、韩国存储配套、InP 衬底为什么会在 AI 周期里变成关键瓶颈。
3. 哪些技术路线一旦切换，会直接重写利润池与 A 股映射顺序。

---

## 二、日本材料链：不能只写成“光刻胶”

### 1. 事实

1. `ASML`
   - 2025 年官方年报披露总净销售额 `327` 亿欧元，毛利率 `52.8%`。
2. `TOK`
   - 官方 FY2025 Q&A 明确：HBM 带动存储需求稳健，ArF / KrF 光刻胶稳定增长，EUV 光刻胶从 2025 下半年开始全面贡献销售，FY2025 同比增长约 `50%`。
3. `JSR`
   - 官方可持续页面披露 EUV 光刻已显著推动先进半导体微缩，MOR 被明确写成支持未来微缩的下一代关键材料，并预计自 `2025` 年前后开始导入量产。
4. `Fujifilm`
   - 官方 `2024-10-29` 新闻稿披露开始销售 EUV resist 与 EUV developer，并将在日本静冈和韩国平泽增强产能与质量评估功能。
5. `HOYA`
   - 官方 FY2025 信息技术业务收入同比增长 `36%`，明确受半导体 photomask blanks 需求恢复带动；公司主页将高精度 mask blanks 列为核心技术产品线。
6. `Shin-Etsu Chemical`
   - 2025 年报披露电子材料业务 CapEx `2455.44` 亿日元，其中包括提升硅片质量要求、强化光刻胶制造设施与半导体材料产线。
7. `Mitsui Chemicals`
   - 官方 `2024-05-28` 披露将在岩国大竹工厂建设面向 `next-gen High-NA, high-output EUV lithography systems` 的 `CNT pellicles` 产线，规划产能 `5,000 sheets per year`，预计 `2025-12` 完工。
8. `ADEKA`
   - 官方半导体材料页明确其提供 `high-purity chlorine`、`HBr`、`BCl3`，并持续开发 `ALD and CVD precursors`，用于 `High-k`、`ferroelectric`、`electrode`、`wiring`、`barrier metal`、`dielectric film` 与 `Cu`。
9. `SCREEN`
   - 官方产品与新闻页面明确其研发重点覆盖 `post etch`、`pre-deposition`、`pre-lithography`、`post CMP cleans` 与 `selective wet etch`；官方口径明确 `over 30% of all semiconductor manufacturing steps` 涉及 `wet cleans`。
10. `TOPPAN`
   - 官方电子业务页明确其覆盖 `FC-BGA substrate`、`Next-Generation package substrate`；官方 `2025-12-10` 新闻稿披露与 Tekscend Photomask 展示 `semiconductor photomasks`、`advanced semiconductor packaging utilizing large glass panels` 与 `FC-BGA substrates`。

### 2. 判断

这说明全球 AI 芯片制造主链并不是“只有先进制程代工才重要”，而是至少包括七层：

1. `光刻设备瓶颈`
   - 由 ASML 代表。
2. `光刻材料与硅片瓶颈`
   - 由 TOK、JSR、Fujifilm、Shin-Etsu 代表。
3. `掩模 blank / 掩模配套瓶颈`
   - 由 HOYA 代表。
4. `材料路线代际升级`
   - 由传统 EUV resist 向 MOR 等下一代材料延伸。
5. `良率与稳定量产能力`
   - 真正决定利润能否从故事走到财报。
6. `pellicle / photomask / 清洗工艺`
   - 属于先进 EUV 良率与生产连续性的隐性瓶颈。
7. `前驱体 / 特气 / advanced wet chemistry`
   - 属于先进节点从研发转向量产时最容易被低估的化学工艺节点。

### 3. 对 A 股的意义

这条链对 A 股的启发是：

1. 半导体材料不该只按“国产替代主题”写。
2. 更应该问：
   - 谁对应高端光刻胶？
   - 谁对应 EUV developer 与高端溶剂体系？
   - 谁对应湿电子化学品？
   - 谁对应硅片、掩模 blank、CMP 材料？
   - 谁是真正跟随全球先进制程扩产的高纯度配套？

---

## 三、韩国存储链：不只是 HBM 芯片，而是整条“存储 + 设备 + 基板”系统

### 1. 事实

1. `SK hynix`
   - FY2025 官方披露收入 `97.1467` 万亿韩元、营业利润 `47.2063` 万亿韩元。
   - 官方 `2025-09-12` 披露已完成 HBM4 开发并准备量产，带宽较前代翻倍、功耗效率提升 `40%+`。
2. `Samsung Electronics`
   - FY2025 官方披露年收入 `333.6` 万亿韩元。
   - 官方 1Q2025 披露明确提到将 ramp-up `enhanced HBM3E 12H`，并加速 `8th Gen V-NAND`。
3. `Micron`
   - 官方材料把 2028 年 HBM TAM 上修到约 `1000` 亿美元。
   - 官方 `2026-03-16` 披露已经量产出货 `HBM4 36GB 12H`，面向 NVIDIA Vera Rubin。
4. `Hanmi Semiconductor`
   - 官方产品线已把 `HBM TC BONDER` 列为核心品类。
   - 官方新闻稿披露 `TC BONDER 4` 为 HBM4 专用设备，并强调生产效率与精度升级。
5. `Samsung Electro-Mechanics`
   - 官方 4Q2025 earnings release 写明 FCBGA 收入受 AI/server 和 automotive substrate 需求带动。
   - 官方 CES 2025 口径写明正在开发 `glass material semiconductor substrate`。
6. `Ibiden`
   - 官方 Integrated Report 2025 明确 IC package substrate 是其核心业务，且该业务需要持续资本开支与财务结构配合。
7. `Nepes`
   - 官方 `2025-11-19` 新闻稿披露其在 ISMP 2025 展示 `Fan-Out Embedded Bridge Interposer for Scalable Heterogeneous Integration of NPUs and HBMs`，把 `NPUs and HBMs` 异构集成写成重点展示方向。
8. `ISC`
   - 官网 API `2026-04` 产品页明确存在 `Memory Test Socket`、`Burn in Test Socket` 与 `System IC Test Socket` 三条产品线。
   - `Memory Test Socket` 明确适用于 `all memory devices and packages`，支持 `0.2P~1.0P`，强调 `High Speed`、`High Voltage Test Solution` 与 `No Ball Damage`。
   - `Burn in Test Socket` 明确面向 `LPDDR / NAND Flash`，并覆盖 `DC BI Socket / Normal BI Socket / High Speed BI Socket`。
   - `System IC Test Socket` 明确覆盖 `AP / CPU / GPU / CPO / RF / PMIC / Sensor & Mixed Signal`，并支持 `Validation / SLT / ATE / Burn-in Test`，等于把 AI / HPC 系统芯片测试直接写进产品页。
   - `iSP` 分类下新增 `Pyramid PIN / Pogo Socket / Coaxial Socket`，其中 `Pyramid PIN` 明确写明 `MEMS process`、`high hardness (Hv1000)` 与 `customized solutions for each customer`，意味着 `contactor / probe head` 这一更细节点已经有官方产品样本。
9. `Okins Electronics`
   - 官方 BiTS Division 页面明确其产品覆盖 `test socket`、`burn-in socket`、`spring probes` 与 `interface boards`，并把 `Package Final Test` 单列。
   - 官方历史页披露 `1999` 年 `Burn-In Socket Approved by Samsung and SK hynix`，`2025` 年开始供应 `LPDDR5 burn-in socket`。
   - 官方新闻页摘要披露 `Q2` 增长驱动包括 `LPDDR5 burn-in sockets` 与 `memory burn-in` 需求。
10. `SEMES`
   - 官方 `2026-02-24` 新闻稿披露：`TC bonder` 已向客户供货以满足 `HBM` 需求。
   - 同一新闻稿明确，公司正在开发高精度高生产性的 `hybrid bonder`，并已在客户处进行 `demo evaluation`。
   - 官方产品页已将 `TC Bonder` 单列为核心封装设备。

### 2. 判断

这组事实说明：

1. HBM 不是“单颗存储芯片”的逻辑。
2. 它本质上是一条：

`高性能 DRAM -> 堆叠 -> TC bonding -> 测试 -> package substrate -> system validation`

的复合制造链。

也就是说，韩国 HBM 与测试 / 封装配套簇至少要固定拆成六段看：

1. `HBM / DRAM`
2. `TC bonding`
3. `memory test socket / burn-in socket / AI system IC socket`
4. `package final test`
5. `bridge interposer / fan-out`
6. `FCBGA / ABF / glass`

### 3. 对 A 股的意义

这条链给 A 股的最大启发不是“跟 HBM 就行”，而是要进一步区分：

1. 存储代理 / 模组
2. 封测与先进封装
3. TC bonder / hybrid bonder / memory test 设备
4. 封装基板
5. 测试、burn-in、热管理材料

当前更准确的保守口径应是：

1. `ISC + Okins Electronics`
   - 已经把 `memory test socket / burn-in socket / package final test / AI system IC socket` 这条韩国测试链主干补成第一版正式样本。
2. `contactor`
   - 已通过 `ISC iSP` 分类补出官方产品样本，当前状态应写成 `已验证节点，经营待补`，不再写成节点空白。
3. `hybrid bonding`
   - 已通过 `SEMES` 官方新闻稿补出开发样本，当前状态应写成 `已验证节点，经营待补`，不再写成节点空白。
4. `Nepes`
   - 目前更像“系统级桥接封装已出现明确官方技术方向”，还不是“经营层已经形成连续兑现”的结论。
5. `glass / TGV`
   - 当前仍主要停留在 `技术路径确认`，量产客户与经营连续验证最弱。

---

## 四、InP 衬底与光通信：AI 互连升级不只是硅光一个词

### 1. 事实

1. `Sumitomo Electric`
   - 官方总裁致辞明确提出，将增强 `optical devices` 与 `indium phosphide (InP) substrates` 产能。
   - 官方数据中心业务增长材料显示，InP substrate 产能也在扩张。
2. `Coherent`
   - 2025 年报写明，公司拥有多座 InP fabs，并正向 `6-inch wafer capability` 推进。
   - 官方材料写明获得资金以扩大 InP 产能。

### 2. 判断

这说明 AI 光互连升级里，至少有两层不能被省略：

1. `光模块 / 光器件系统层`
2. `InP 衬底 / 外延 / EML / DML / CW laser` 上游基础材料层

也就是说，未来如果 200G / lane、coherent optics、ZR / ZR+、高速 EML 路线继续强化，InP 相关上游的重要性会高于市场当前常规理解。

### 3. 对 A 股的意义

A 股后续不应只写“光模块龙头”，还要继续向上问：

1. 谁对应光芯片和材料。
2. 谁对应衬底、外延、封装与检测。
3. 谁的逻辑只是可插拔模块，谁可能吃到上游化合物半导体升级。

---

## 五、先进封装基板链：ABF 与玻璃不是同一个阶段

### 1. 事实

1. `Samsung Electro-Mechanics`
   - 官方 4Q2025 披露 FCBGA 收入受 AI/server 需求带动。
   - 官方 CES 2025 口径披露正在开发玻璃材料半导体基板。
2. `Ibiden`
   - 官方 2025 综合报告明确 IC package substrate 是其核心业务，需要持续资本开支与融资配合。
   - 官方产品页说明 flip-chip package substrate 已成为高性能芯片的重要组成。
3. `Intel`
   - 官方披露玻璃基板具备更细线路、更大封装尺寸、更高 I/O 密度，并可缓解有机基板 warpage 问题。

### 2. 判断

这说明先进封装利润池至少分三层：

1. `OSAT / 封装平台`
2. `ABF / FCBGA 基板`
3. `glass core / glass substrate` 下一代路线

如果只跟踪 OSAT，而不跟踪高端基板与玻璃路线，就会错过下一轮利润池迁移。

这也是为什么本轮必须补一张：

[AI全球芯片制造深链与A股映射总表_第一版](</F:/股票/ai-industry-cycle-research/03_结果层/01_总表整合与AI映射/AI全球芯片制造深链与A股映射总表_第一版.md>)

因为没有这一步，制造深链就仍然停留在“海外样本研究”，还没有真正回到本仓库要解决的 A 股承接问题。

---

## 六、技术路线之争：路线切换会重写利润池

### 1. CPO vs 可插拔光模块

#### 事实

1. `Broadcom`
   - 官方 `2025-05-15` 发布第三代 `200G/lane` CPO。
   - 同时强调二代 `100G/lane` CPO 生态、OSAT 工艺、热设计和良率成熟。
   - 官方技术页明确 CPO 目标是提升带宽密度和功耗效率。

#### 判断

当前更准确的口径不是“CPO 已完全替代可插拔”，而是：

1. `CPO` 已从概念进入工程成熟度快速提升阶段。
2. 但可插拔模块仍未被立即淘汰。
3. 后续要观察的是：
   - 良率
   - 热管理
   - 维护复杂度
   - 光纤路由和生态适配

### 2. Organic substrate vs Glass substrate

#### 事实

1. `Intel`
   - 官方披露玻璃基板具备更细线路、更大封装尺寸、更高 I/O 密度，并可显著缓解有机基板的 warpage 问题。
2. `Samsung Electro-Mechanics`
   - 官方 CES 2025 披露正在开发以玻璃为 core 的半导体基板，认为其在 AI accelerators、server CPU 等高端产品具备潜力。

#### 判断

当前更准确的口径不是“玻璃路线已赢”，而是：

1. `organic substrate` 仍是现实主线。
2. `glass substrate` 已成为下一代高端封装的重要候选路线。
3. 真正决定胜负的不是故事，而是：
   - 量产良率
   - 成本
   - 生态重构难度
   - 与 chiplet / 高 I/O / 光电融合的适配度

### 3. HBM4 持续强化 vs 其他内存层级补位

#### 事实

1. `SK hynix`
   - 已完成 HBM4 开发并准备量产。
2. `Samsung Electronics`
   - 继续强化 HBM3E 12H。
3. `Micron`
   - 已开始量产 HBM4 36GB 12H。

#### 判断

这意味着：

1. HBM 主线短期仍在加强，而不是削弱。
2. 但越往后，市场越会从“谁有 HBM”切到“谁能把 HBM 做成持续利润和系统级供给能力”。

### 4. InP 光器件 vs silicon photonics / CPO

#### 判断

当前更像：

1. `InP` 在高端光源和高速传输侧仍有关键位置。
2. `silicon photonics / CPO` 则代表系统级互连升级路径。
3. 两者短期更可能共存，而不是立刻单边替代。

### 5. 传统 EUV resist vs MOR 等下一代材料

#### 事实

1. `JSR`
   - 官方明确 MOR 是支持未来微缩的重要下一代材料，并预计自 `2025` 年前后开始走向量产应用。
2. `TOK / Fujifilm`
   - 官方材料继续强化 EUV resist / developer 主线，并推动更成熟的量产体系。

#### 判断

当前不是“传统胶马上被替代”，而是：

1. `传统 EUV resist` 仍是现实量产主线。
2. `MOR` 是下一代高分辨率重要选项。
3. 这意味着日本材料链内部也存在代际竞争，不能把“光刻胶”写成静态篮子。

---

## 七、路线之争对 A 股映射的直接影响

| 路线 | 若强化，A 股更容易受益的方向 | 若弱化，最容易先掉队的方向 |
|---|---|---|
| HBM4 持续强化 | 存储代理、先进封装、测试与高端基板 | 纯通用存储修复叙事 |
| CPO / silicon photonics 升级 | 光引擎、封装、化合物半导体上游、部分硅光配套 | 只吃可插拔模块涨价的被动配套 |
| glass substrate 升级 | 玻璃基板、TGV、玻璃加工与载板配套 | 只有概念没有客户验证的题材外溢 |
| MOR 升级 | 高端光刻材料、平台型化学品与先进胶材 | 仅有低端替代逻辑、缺先进制程绑定的材料公司 |

---

## 八、为什么当前产业地图仍要继续下钻

虽然全景图已经写出了：

1. 光刻胶
2. 存储链
3. 先进封装
4. 光互连

但如果不继续补以下关键节点，地图仍会显得偏“树状目录”，而不是研究地图：

1. `日本光刻胶 / 显影液 / photomask blank`
2. `韩国 HBM / DRAM / NAND / TC bonder / contactor / hybrid bonding / substrate`
3. `InP substrate / EML / CW laser`
4. `ABF / FCBGA / glass core`
5. `CPO / pluggable / silicon photonics`
6. `MOR / 传统 EUV resist`

---

## 九、轻量复评

按 `$industry-logic-scorer` 的口径，这次新增内容主要补强了四件事：

1. `核心变量拆解`
   - 不再把制造链压成“代工 + GPU”两段式，而是拆成日本材料、韩国 HBM 配套、InP、基板和路线之争五段。
2. `传导链完整度`
   - 把设备、材料、存储、封装基板、互连和路线之争串起来了。
3. `资本周期与供给审计`
   - 把 CapEx、良率、产能和材料设施投入纳入了判断。
4. `证伪条件`
   - 路线之争部分开始具备“谁会赢、靠什么赢、什么情况会输”的审计框架。

仍未补满的部分：

1. 日本材料链二线样本的连续财务验证
2. 韩国 HBM `contactor / hybrid bonding` 已有节点级官方样本，但经营连续验证仍弱
3. 这条全球制造深链自己的估值 / 预期 / 拥挤表
4. 新增 A 股映射表后的持续回写机制

轻量分数判断：

1. 相比上一版全球样本层，这一补强可把“全球制造深链”研究质量从“结构已立但偏浅”抬到 `90/100` 左右。
2. 当前仍不宜宣称达到 `91-92/100`；主因已从“节点空白”转向“经营连续验证、A 股承接纯度与估值链系统化仍不足”。

---

## 十、配套入口

1. [AI全球芯片制造与材料链样本池_第一版](</F:/股票/ai-industry-cycle-research/02_桥接层/02_AI产业链研究卡/AI全球芯片制造与材料链样本池_第一版.md>)
2. [AI全球芯片制造深链与A股映射总表_第一版](</F:/股票/ai-industry-cycle-research/03_结果层/01_总表整合与AI映射/AI全球芯片制造深链与A股映射总表_第一版.md>)
3. [AI全球产业链核心样本池_第一版](</F:/股票/ai-industry-cycle-research/02_桥接层/02_AI产业链研究卡/AI全球产业链核心样本池_第一版.md>)
4. [AI产业链全景图正式版_第一版](</F:/股票/ai-industry-cycle-research/03_结果层/01_总表整合与AI映射/AI产业链全景图正式版_第一版.md>)

---

## 十一、来源

1. ASML 2025 Annual Report：<https://www.asml.com/investors/annual-report/2025>
2. TOK FY2025 Q&A Summary / Semiconductor products page：<https://www.tok.co.jp/application/files/4017/7097/4316/q4_QA_Summary_en.pdf> 、<https://www.tok.co.jp/eng/products/semiconductor-pre>
3. JSR Report 2025 / EUV page：<https://www.jsr.co.jp/jsr_e/ir/assets/pdf/2025_e_all.pdf> 、<https://www.jsr.co.jp/jsr_e/sustainability/materiality/well-being.html>
4. Fujifilm semiconductor materials / EUV official：<https://www.fujifilm.com/us/en/business/semiconductor-materials> 、<https://www.fujifilm.com/jp/en/news/hq/11842>
5. HOYA Report 2025 / corporate site：<https://www.hoya.com/ir/2025/en/highlight/> 、<https://www.hoya.com/en/>
6. Shin-Etsu Annual Report 2025 / FY2025 financial materials：<https://www.shinetsu.co.jp/en/ir/ir-data/ir-annual/> 、<https://www.shinetsu.co.jp/wp-content/uploads/2025/07/Financial-Section.pdf>
7. Mitsui Chemicals EUV pellicle official：<https://jp.mitsuichemicals.com/en/release/2024/2024_0528_1/index.htm>
8. ADEKA semiconductor materials official：<https://www.adeka.co.jp/en/chemical/products/semicon/index.html>
9. SCREEN products / wet clean R&D official：<https://www.screen.co.jp/en/products> 、<https://www.screen.co.jp/en/news/NR251216E>
10. TOPPAN semiconductor package substrate / photomask official：<https://www.toppan.com/en/electronics/> 、<https://www.holdings.toppan.com/en/news/2025/12/newsrelease251210_1.html>
11. SK hynix FY2025 / HBM4 official：<https://news.skhynix.com/sk-hynix-announces-fy25-financial-results/> 、<https://news.skhynix.com/sk-hynix-completes-worlds-first-hbm4-development-and-readies-mass-production/>
12. Samsung Electronics FY2025 / 1Q2025：<https://news.samsung.com/global/samsung-electronics-announces-fourth-quarter-and-fy-2025-results> 、<https://news.samsung.com/global/samsung-electronics-announces-first-quarter-2025-results>
13. Micron HBM4 / earnings materials：<https://investors.micron.com/news-releases/news-release-details/micron-high-volume-production-hbm4-designed-nvidia-vera-rubin> 、<https://investors.micron.com/static-files/530bd7ed-a8c8-4687-af4a-8c129f740e09>
14. Hanmi Semiconductor HBM TC bonder official：<https://www.hanmisemi.com/index.php?action=SiteProductEn&module=Html&sSubNo=2> 、<https://www.hanmisemi.com/index.php?CurrentPage=1&action=SiteBoardEn&iBrdContNo=253&iBrdNo=5&module=Board&sBrdContRe=0&sMode=VIEW_FORM&sSearchField=&sSearchValue=>
15. Samsung Electro-Mechanics earnings / package substrate / glass substrate：<https://m.samsungsem.com/resources/file/global/ir/earnings_release/4Q25_Earnings_Release_eng.pdf> 、<https://m.samsungsem.com/global/product/substrate/package-substrate.do> 、<https://m.samsungsem.com/global/newsroom/news/view.do?id=8922>
16. Ibiden Integrated Report 2025 / package substrate：<https://www.ibiden.com/ir/items/IntegratedReport2025_en.pdf> 、<https://www.ibiden.com/product/electronics/merchandise/fliptippkg/>
17. Nepes ISMP 2025 official：<https://www.nepes.co.kr/en/ir/ir_news.php?bgu=view&code=news&idx=1116>
18. ISC official API product pages：<https://isc21.kr/api/board/list>
19. Okins Electronics official：<https://okins.co.kr/en/business01/> 、<https://okins.co.kr/en/business02/> 、<https://okins.co.kr/en/history/> 、<https://okins.co.kr/en/news/?mod=document&pageid=2&uid=119>
20. SEMES official hybrid bonding / TC bonder：<https://www.semes.com/en/media/newsroom/detail/123> 、<https://www.semes.com/en/product/semiconductor/package/package?tab=tc-bonder>
21. Sumitomo Electric president message / growth strategy / InP：<https://sumitomoelectric.com/ir/management/greeting> 、<https://sumitomoelectric.com/sites/default/files/2025-11/download_documents/Growth%20strategy%20for%20data%20center-related%20business_2025.pdf> 、<https://sumitomoelectric.com/id/project/v27/03>
22. Coherent annual report / investor presentation：<https://www.coherent.com/content/dam/coherent/site/en/documents/investors/annual-filings/2025/coherent-annual-report-2025.pdf> 、<https://www.coherent.com/content/dam/coherent/site/en/documents/investors/investor-presentations/2025/february-5/investor-presentation-20250205.pdf>
23. Broadcom CPO official：<https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-third-generation-co-packaged-optics-cpo> 、<https://www.broadcom.com/info/optics/cpo>
24. Intel glass substrate official：<https://download.intel.com/newsroom/archive/2025/en-us-2023-09-18-intel-unveils-industryleading-glass-substrates-to-meet-demand-for-more-powerful-compute.pdf> 、<https://community.intel.com/t5/Blogs/Intel-Foundry/Systems-Foundry-for-the-AI-Era/Intel-Foundry-s-Advanced-Packaging-Enables-Next-Gen-Technologies/post/1719719>
