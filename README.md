# 医学统计Skills（medstats-pharm-skills）

面向**药学本科生**医学统计学学习与实验的开源 Agent Skill 集合。把统计方法的选择纪律、前提条件、软件操作与报告规范写成 agent 可执行的 Markdown 约定，让学生在 AI 助手辅助下完成"从数据到可复跑的统计分析文件"的全过程。

设计参考：John M. Barrios 的 [barrios-skills](https://github.com/Barrios88/barrios-skills)（面向经济/会计研究者）。本仓库将其"skill=约定、产物落盘、验证闸门、iron-law 清单"的做法移植到本科医学统计教学，对象从研究者换成学生，验证闸门从"研究结果可信"换成"方法用对、前提验过、数字来自文件"。

## 一条规则先记住

**对话是可丢弃的上下文。** 数据、代码、统计输出、表、图、方法决策都必须落成文件；报告正文里的每个统计数字必须能在输出文件中找到，禁止手打。

## v0.1 包含什么

| 模块 | 内容 |
|---|---|
| `skills/reporting/method-selection-router` | 方法选择总路由：五步（研究目的→资料类型→设计类型→组数→前提）定方法 |
| `skills/methods-core/t-test` | 单样本/配对/两独立样本 t 检验，含 SPSS/R/Python 三轨与生物等效性对数尺度例题 |
| `skills/methods-core/chi-square` | 四格表/R×C/McNemar，适用条件链、OR 与报告模板 |
| `datasets/teaching/` | 3 个药学场景模拟数据集（含量测定、BE 交叉试验、不良反应），固定随机种子可复跑 |
| `templates/student-project/` | 学生分析项目目录模板（data/raw、output、DECISIONS.md、LOG.md） |

后续规划见仓库根目录《医学统计Skills_设计方案》。

## 快速开始

1. 下载本仓库（GitHub / Gitee 镜像，见 [install/](install/)）；
2. 把需要的 skill 文件夹复制到你的 agent 的技能/规则目录，或直接把 `SKILL.md` 内容提供给 agent；
3. 分析任何数据，第一句话都走 `method-selection-router`；
4. 按学生项目模板建目录，把数据放进 `data/raw/`。

## 浏览全部 skill

### methods-core/ —— 统计方法核心（对应教材章节）

| Skill | 状态 | 说明 |
|---|---|---|
| data-types-and-summary | 规划中 | 计量/计数/等级资料识别与统计描述 |
| statistical-tables-graphs | 规划中 | 三线表与统计图选择 |
| [t-test](skills/methods-core/t-test) | ✅ v0.1 | 单样本/配对/独立样本 t 检验 |
| anova | 规划中 | 完全随机、随机区组设计方差分析与多重比较 |
| [chi-square](skills/methods-core/chi-square) | ✅ v0.1 | 四格表、R×C、McNemar |
| nonparametric | 规划中 | 符号秩、Mann–Whitney U、Kruskal–Wallis |
| correlation-regression | 规划中 | 直线相关与回归 |
| logistic-regression | 规划中 | 二分类结局、调整 OR |
| survival-analysis-intro | 规划中 | Kaplan–Meier、log-rank |
| sample-size-design | 规划中 | 样本量估算、随机化与对照 |

### pharm-applications/ —— 药学专门场景

| Skill | 状态 | 说明 |
|---|---|---|
| bioequivalence | 规划中 | 双单侧检验、90%CI、80–125% 界值 |
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
| [method-selection-router](skills/reporting/method-selection-router) | ✅ v0.1 | 方法选择总路由 |
| stats-report-writing | 规划中 | 实验报告结构与结果段写法 |
| result-interpretation | 规划中 | P 值、CI、效应量与常见误读 |

### optional/

SPSS 菜单对照、考试自查题、错题模式等，按需安装。

## 验证闸门（每个分析都要过）

1. 先定资料类型（计量/计数/等级），再谈方法；
2. 参数检验前必须验正态性与方差齐性，不达标转非参数并在 DECISIONS.md 写理由；
3. 卡方先过条件链：n≥40？理论频数 ≥5？不满足转校正/Fisher；
4. 两组比较先判定配对还是独立（以数据结构为证）；
5. 只报 P 值不合格——必须同时给效应量与 95% CI；
6. P<0.05 ≠ 有专业意义；P≥0.05 ≠ 无差别；
7. 多重比较必须说明校正方法；
8. 正文每个统计数字必须能在输出文件中找到；
9. 统计表一律三线表，统计图注明 n 与误差线含义（SD/SEM）；
10. 每次分析更新 LOG.md 与 DECISIONS.md。

## 教学数据合规

仓库**不收录任何真实受试者数据**（脱敏也不收）。教学数据集全部由固定随机种子的脚本生成；未来引入真实数据仅限已公开发表、许可清晰且无个体信息的汇总数据。学生把课程数据交给 AI 前须按学校与《个人信息保护法》要求脱敏，具体规范以任课教师要求为准。

## 软件环境

- SPSS（课堂主机位，三轨之一）；
- R 4.x（自带 `chisq.test`、`t.test`、`mcnemar.test`）；
- Python 3.10+：numpy、pandas、scipy、statsmodels（`pip install numpy pandas scipy statsmodels`）。

## 许可

双协议：

- **代码**（`.py`/`.R`/`.sh` 及文档中的代码片段）：[MIT](LICENSE)；
- **文字与教学内容**（SKILL.md 等 Markdown 文档、数据字典、模板文本）：[CC BY 4.0](LICENSE-CONTENT.md)，可自由转载、改编、翻译、用于教材出版与教学，署名「ASUO」并注明本仓库即可。

贡献内容即表示你同意以同样的双协议发布。
