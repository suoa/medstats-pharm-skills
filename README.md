# 医学统计Skills（medstats-pharm-skills）

面向**药学本科生**医学统计学学习与实验的开源 Agent Skill 集合。把统计方法的选择纪律、前提条件、软件操作与报告规范写成 agent 可执行的 Markdown 约定，让学生在 AI 助手辅助下完成"从数据到可复跑的统计分析文件"的全过程。

设计参考：John M. Barrios 的 [barrios-skills](https://github.com/Barrios88/barrios-skills)（面向经济/会计研究者）。本仓库将其"skill=约定、产物落盘、验证闸门、iron-law 清单"的做法移植到本科医学统计教学，对象从研究者换成学生，验证闸门从"研究结果可信"换成"方法用对、前提验过、数字来自文件"。

## 一条规则先记住

**对话是可丢弃的上下文。** 数据、代码、统计输出与方法决策要留成文件；报告数字须能定位到本次真实输出。脚本路线自动生成结果；SPSS 菜单路线允许准确转录，并标注输出文件、表名及行列。课堂手算可另附过程，不能用参考答案冒充软件运行。

## 当前包含什么（v0.2 限定教学试用候选）

| 模块 | 内容 |
|---|---|
| `skills/reporting/method-selection-router` | 先明确问题与独立/相关结构，再形成候选方法、检查相应条件并记录决策 |
| `skills/methods-core/t-test` | 单样本/配对/两独立样本 t 检验，含 SPSS/R/Python 三轨与配对对数数据的等效界值演示 |
| `skills/methods-core/chi-square` | 四格表/R×C/McNemar，适用条件链、OR 与报告模板 |
| `datasets/teaching/` | 3 个药学场景模拟数据集（含量测定、配对 Cmax、不良反应），固定随机种子可复跑；不支持正式 BE 评价 |
| `templates/student-project/` | 学生分析项目目录模板（data/raw、output、DECISIONS.md、LOG.md） |

版本范围见 [COLLECTION.md](COLLECTION.md)，历史设计见 [设计方案](docs/设计方案_v0.1.md)，变更见 [CHANGELOG.md](CHANGELOG.md)。规划中的目录不代表已经发布可执行技能。

## 快速开始

1. 从 GitHub 下载本仓库（Gitee 镜像筹备中，见 [install/](install/)）；
2. 按平台说明复制完整 skill 文件夹，保留 `references/`；教学数据与根目录 `scripts/` 需另行保留。仅粘贴 Markdown 不会赋予 agent 运行代码或保存文件的能力；
3. 按 [学生项目模板](templates/student-project/) 建目录。按课程规定实际使用AI时，把题目、数据路径、是否同一对象多次测量及教师的软件要求交给 router；不用AI时按教材和教师指引核查，已有信息不用重复填写；
4. 每份作业选一条软件路线即可。主要规则和比较方向在查看检验结果前写明，再运行和保存结果。

仓库自带数据可先走 Python 示例闭环（在仓库根目录运行，不会重新生成或改写 CSV）：

```bash
python -m pip install -r requirements-teaching.txt
python scripts/analyze_teaching.py --output-dir output/teaching
python -m unittest discover -s tests -v
```

参考答案用于核对；学生报告必须引用自己的本次输出。数据生成命令仅供维护者重建合成数据，与分析命令分开。

分析还保存 `diagnostics.png` 与 `diagnostic_points.csv`：分别画两组含量数据和完整对的 `ln(T)−ln(R)` 差值，作图点保留个体标识并与本次分析集一致。打开图形后，在 `DECISIONS.md` 记一句对尾部、弯曲或异常点的判断；JSON 的 `requires_human_review` 不等于已验过前提。图形不能证明独立性，接近直线也不证明正态。

第一份课堂任务可用 [两药不良事件限定试用作业](docs/teaching-pilot.md)。教师先填写本次软件、正课/课后AI范围与教材口径，再在本课机位走通所选路线。题单含不使用AI的等价操作路径及空白试用记录，AI为可选时不因未使用而判缺交；试用后沿用已有输出证据记录卡点，不增加一套学生日志。

SPSS机房可先用[待实机验收包](docs/spss-machine-check.md)：维护者一条命令生成含原始CSV副本、四份语法、64项参考值及空白运行记录的便携ZIP；学生不需Python/R。每轮用新目录，先人工核对输入，再运行分析和保存SPV/PDF。本轮只核对官方语法资料及打包过程，SPSS尚未实际执行。

## 浏览全部 skill

### methods-core/ —— 统计方法核心（对应教材章节）

| Skill | 状态 | 说明 |
|---|---|---|
| data-types-and-summary | 规划中 | 计量/计数/等级资料识别与统计描述 |
| statistical-tables-graphs | 规划中 | 三线表与统计图选择 |
| [t-test](skills/methods-core/t-test) | 已有，v0.2 修订 | 单样本/配对/独立样本 t 检验 |
| anova | 规划中 | 完全随机、随机区组设计方差分析与多重比较 |
| [chi-square](skills/methods-core/chi-square) | 已有，v0.2 修订 | 四格表、R×C、McNemar |
| nonparametric | 规划中 | 符号秩、Mann–Whitney U、Kruskal–Wallis |
| correlation-regression | 规划中 | 直线相关与回归 |
| logistic-regression | 规划中 | 二分类结局、调整 OR |
| survival-analysis-intro | 规划中 | Kaplan–Meier、log-rank |
| sample-size-design | 规划中 | 样本量估算、随机化与对照 |

### pharm-applications/ —— 药学专门场景

| Skill | 状态 | 说明 |
|---|---|---|
| bioequivalence | 规划中 | 按适用规范进行设计与参数分析；常规界值有适用范围 |
| pharmacokinetics-stats | 规划中 | AUC/Cmax/Tmax 统计处理 |
| assay-validation | 规划中 | 线性、精密度、回收率、耐用性 |
| adverse-event-analysis | 规划中 | 不良事件数据与 ROR 信号入门 |
| clinical-trial-stats | 规划中 | 试验设计、终点、ITT/PP 分析集 |

### data-and-tools/ 与 reporting/

| Skill | 状态 | 说明 |
|---|---|---|
| openfda-data | 规划中 | openFDA API 取数约定（免 key） |
| clinicaltrials-data | 规划中 | ClinicalTrials.gov API v2 |
| python-stats-recipes | 规划中 | scipy/statsmodels 执行模板集 |
| [method-selection-router](skills/reporting/method-selection-router) | 已有，v0.2 修订 | 方法选择总路由 |
| stats-report-writing | 规划中 | 实验报告结构与结果段写法 |
| result-interpretation | 规划中 | P 值、CI、效应量与常见误读 |

### optional/

SPSS 菜单对照、考试自查题、错题模式等，按需安装。

## 验证闸门（每个分析都要过）

1. 先明确研究问题、结局及实验/抽样单位，区分独立、配对、重复、整群等结构；设计不能只凭列名推断；
2. 按候选方法检查前提。配对 t 看差值；单样本与配对 t 不要求两组方差齐。Shapiro–Wilk 的 P>0.05 不证明正态；不按一次前提检验机械换法；
3. 独立二分类表先查编码、频数及零边际，再按预定课程规则选 Pearson/Yates/Fisher；R×C 与 McNemar 分开判断；
4. 在看结果前固定主要策略、软件参数与比较方向，不按较小 P 值挑方法；
5. 不论 P 值大小，报告预定效应及适当的 CI，注明算法与置信水平（通常 95%，等效界值演示为 90%）；区间无法估计时写明原因；
6. P<0.05 ≠ 有专业意义；P≥0.05 ≠ 无差别；
7. 多重比较必须说明校正方法；
8. 正文数字定位到本次输出；精确检验不强填 χ² 和自由度；
9. 报告表按课程要求采用三线表；图注明 n 与误差线含义（SD/SE/CI）；
10. DECISIONS.md 与 LOG.md 复用同一任务信息，分别记实读取、运行、保存与核验状态；不能运行或保存时如实说明。

## 教学数据合规

仓库**不收录任何真实受试者数据**（脱敏也不收）。教学数据集全部由固定随机种子的脚本生成；未来引入真实数据仅限已公开发表、许可清晰且无个体信息的汇总数据。学生把课程数据交给 AI 前须按学校与《个人信息保护法》要求脱敏，具体规范以任课教师要求为准。

## 软件环境

- Python：依赖及测试基线见 [requirements-teaching.txt](requirements-teaching.txt)，实际运行记录见 [验证记录](docs/validation.md)；其他版本需重新运行测试；
- R 4.x：基础R数值复算及文档模板已在 WebR 0.6.0 / R 4.6.0（WebAssembly）实跑；99个数值字段与Python在明示容差内一致。当前mean中心Levene使用基础`stats`，无需`car`。桌面R/Rscript及其他包仍待本机验证，见[验证记录](docs/validation.md)；
- SPSS 25 以上：保留中文菜单与输出核查指引；本轮未在 SPSS 环境实跑，不能据此宣称所有版本界面和精确检验默认值相同。

当前试用范围是现有三份合成数据与明示的教学规则。配对 Cmax 数据缺少序列、周期与 AUC，不能作正式交叉 BE 结论；含量数据没有批次层次与具体品种质量标准，不能据此判定真实工艺优劣或药典合格。

## 许可

双协议：

- **代码**（`.py`/`.R`/`.sh`/`.sps` 及文档中的代码片段）：[MIT](LICENSE)；
- **文字与教学内容**（SKILL.md 等 Markdown 文档、数据字典、模板文本）：[CC BY 4.0](LICENSE-CONTENT.md)，可自由转载、改编、翻译、用于教材出版与教学，署名「ASUO」并注明本仓库即可。

贡献内容即表示你同意以同样的双协议发布。
