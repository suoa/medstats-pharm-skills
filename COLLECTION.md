# 目录索引（COLLECTION）

按课题进度选装，不必全部安装。状态：✅ 已发布 v0.1 ｜ 🟡 v0.2 规划 ｜ ⚪ 待定。

## 统计方法核心（methods-core）

| Skill | 状态 | 触发场景 |
|---|---|---|
| data-types-and-summary | 🟡 | 数据到手第一步：变量类型识别、集中/离散趋势描述 |
| statistical-tables-graphs | 🟡 | 做三线表、选统计图 |
| t-test | ✅ | 单样本、配对、两独立样本均数比较 |
| anova | 🟡 | 三组及以上均数比较、随机区组、多重比较 |
| chi-square | ✅ | 两个率/构成比、R×C、配对四格表 |
| nonparametric | 🟡 | 非正态、等级资料的组间比较 |
| correlation-regression | 🟡 | 两连续变量的相关与直线回归 |
| logistic-regression | 🟡 | 二分类结局的影响因素、调整 OR |
| survival-analysis-intro | 🟡 | 随访资料、Kaplan–Meier、log-rank |
| sample-size-design | 🟡 | 开题前样本量估算与设计选择 |

## 药学专门场景（pharm-applications）

| Skill | 状态 | 触发场景 |
|---|---|---|
| bioequivalence | 🟡 | 生物等效性评价（TOST、对数尺度、90%CI） |
| pharmacokinetics-stats | 🟡 | AUC、Cmax、Tmax 的统计处理 |
| assay-validation | 🟡 | 含量测定方法学验证（线性/精密度/回收率） |
| adverse-event-analysis | 🟡 | 不良反应组间比较、ROR 信号入门 |
| clinical-trial-stats | 🟡 | 平行/交叉设计、终点、分析集 |

## 数据与工具（data-and-tools）

| Skill | 状态 | 触发场景 |
|---|---|---|
| openfda-data | 🟡 | openFDA 公开数据取数（免 key） |
| clinicaltrials-data | ⚪ | ClinicalTrials.gov 注册信息与结果查询 |
| python-stats-recipes | 🟡 | scipy/statsmodels 执行模板 |
| spss-output-to-files | ⚪ | SPSS 输出文件化与版本管理 |

## 报告与方法纪律（reporting）

| Skill | 状态 | 触发场景 |
|---|---|---|
| method-selection-router | ✅ | 任何分析的第一步：方法选择总路由 |
| stats-report-writing | 🟡 | 实验报告结构、结果段、讨论段写法 |
| result-interpretation | 🟡 | P 值/CI/效应量解读、误读纠偏 |
| table-figure-standards | ⚪ | 三线表、图注、SD vs SEM |

## 可选（optional）

| Skill | 状态 | 触发场景 |
|---|---|---|
| exam-self-check | ⚪ | 期末自查题与易错点 |
| formula-cheatsheet | ⚪ | 公式速查（只查不用来代替理解） |
| spss-menu-map | ⚪ | SPSS 中文菜单逐路径对照 |

## 数据集

| 数据集 | 状态 | 配套 skill |
|---|---|---|
| tablet_assay.csv | ✅ | t-test |
| bioeq_cmax.csv | ✅ | t-test（对数尺度 TOST 例题） |
| adverse_events.csv | ✅ | chi-square |

## 版本路线

- **v0.1（当前）**：router + t-test + chi-square + 3 数据集 + 模板与安装文档
- **v0.2**：methods-core 其余 8 个 + report-writing + result-interpretation
- **v0.3**：pharm-applications 5 个 + openfda-data
- **v1.0**：全部规划 skill、教学试用一轮后定稿
