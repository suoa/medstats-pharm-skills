# 目录索引（COLLECTION）

按课题进度选装，不必全部安装。状态：✅ 已有技能（v0.2 修订候选）｜ 🟡 后续规划（尚未发布）｜ ⚪ 待定。空目录不是可调用技能；当前仅 router、t-test、chi-square 有 SKILL.md。

## 统计方法核心（methods-core）

| Skill | 状态 | 触发场景 |
|---|---|---|
| data-types-and-summary | 🟡 | 数据到手第一步：变量类型识别、集中/离散趋势描述 |
| statistical-tables-graphs | 🟡 | 做三线表、选统计图 |
| t-test | ✅ | 单样本、配对、两独立样本均数比较 |
| anova | 🟡 | 三组及以上均数比较、随机区组、多重比较 |
| chi-square | ✅ | 两个率/构成比、R×C、配对四格表 |
| nonparametric | 🟡 | 按研究目标及方法假设选择秩方法，不把非正态自动等同于改做秩检验 |
| correlation-regression | 🟡 | 两连续变量的相关与直线回归 |
| logistic-regression | 🟡 | 二分类结局的影响因素、调整 OR |
| survival-analysis-intro | 🟡 | 随访资料、Kaplan–Meier、log-rank |
| sample-size-design | 🟡 | 开题前样本量估算与设计选择 |

## 药学专门场景（pharm-applications）

| Skill | 状态 | 触发场景 |
|---|---|---|
| bioequivalence | 🟡 | 按适用规范核对设计、分析参数、对数尺度及等效界值；现有配对例不代替正式 BE |
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
| bioeq_cmax.csv | ✅ | t-test（配对对数数据等效界值演示；不支持正式 BE 评价） |
| adverse_events.csv | ✅ | chi-square |

## 版本路线

- **v0.1（已发布基线）**：router + t-test + chi-square + 3 数据集 + 模板与安装文档。
- **v0.2（当前整改候选）**：修现有三项技能及参考例题；补只读分析脚本、真实输出与数值/边界验收；修安装和试用声明。Python已验收，基础R数值及模板已有WebAssembly环境实跑；桌面R与SPSS仍待本机验证。先完成限定作业，不在本轮承诺补齐其他方法。
- **v0.2 试用后的第一批新增**：数据描述、图表、报告写作、结果解读，按一次作业的完整链路验收。随后根据课堂任务补 anova、nonparametric、correlation-regression。
- **后续药学应用**：优先补齐真实 BE 设计与模型、药动学、方法学验证等。溶出度、稳定性和剂量探索先作为这些模块的明确场景评估，不立即拆更多技能。
- **v1.0**：以实际课堂使用、维护能力与验收记录确定范围，不以达到固定技能数作为完成标准；继续采用本地计算，暂不自研 MCP。

软件验证与尚待核实事项见 [docs/validation.md](docs/validation.md)，八个路由案例见 [docs/router-case-acceptance.md](docs/router-case-acceptance.md)。
