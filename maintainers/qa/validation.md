# v0.1.1 验证记录（原 v0.2 候选拆分而来）

> 归档说明：本记录原对应 PR #1 的"v0.2 限定教学试用候选"。经拆分合并，统计修正进入 v0.1.1，工程脚本与测试移入 `maintainers/`；下文命令中的路径已同步更新。日期：2026-10-18。修订基线：`9fe0a2705db79c9067ebd9ed3f8d2a03d2620f4c`。不能把这一记录推广为所有软件、数据或设计已验证。

## 实际运行

以下命令从仓库根目录运行。分析脚本只读取现有 CSV；数据生成在隔离临时目录另验，不在学生分析时重建数据。

```bash
python maintainers/scripts/analyze_teaching.py --output-dir output/teaching --t-policy course
python -m unittest discover -s maintainers/tests -t . -v
```

以上是首轮示例路径。共用Python分析命令现在要求输出目录尚不存在，空目录也拒绝；复跑须改用新目录，并同步下游读取结果及R复核命令的Python摘要路径。

Python 基线：Python 3.12.14、NumPy 2.3.5、pandas 2.2.3、SciPy 1.17.0、Matplotlib 3.10.8。具体依赖与实际输出中的版本信息一起核对；最新在线文档版本可能高于本轮实跑版本。

还创建了复用系统预装包的独立 venv，实际执行 `python -m pip install -r maintainers/requirements-teaching.txt` 成功（新增安装statsmodels 0.15.0等依赖），随后在该环境运行分析命令和全部19项测试均通过。此验收覆盖当前运行环境，不代表所有操作系统或完全空白环境均安装通过。

上述命令当前已执行通过：**28项 unittest（22项数值/边界/图形数据检查、2项输出目录保护检查、2项技能分发检查、2项SPSS打包溯源与拒绝覆盖检查）**。另运行 `--t-policy welch`，结果及图形正常保存到独立目录；三个技能此前均通过 skill-creator 的 `quick_validate.py` 格式核验；后续R模板改动已另行实跑核对，`git diff --check` 通过。三份原始 CSV 相对基线的字节未变；固定种子重建在临时目录逐表比较通过，不要求尾空行等格式字节相同。

| 复算项 | 本次结果 | 方法与方向 |
|---|---|---|
| 含量均数差 | 0.760000 个百分点；95%CI 0.101866621～1.418133379 | B−A，pooled |
| 含量主要检验 | t=2.337732158，df=38，P=.0247676045 | 课程Levene(mean)路线，Levene P=.3954279325 |
| Welch 对照 | df=37.359337924，P=.0248629773；95%CI .101495789～1.418504211 | 事先选择Welch时使用对应区间 |
| 配对对数演示 | t=−.623891536，P=.5388380307；GMR=98.097725707%，90%CI 93.056237575%～103.412345477% | ln(T)−ln(R)，24完整对；正式BE未评估 |
| 不良事件主要检验 | χ²=9.230769231，df=1，P=.0023798165 | 未校正Pearson，事件优先表 |
| Fisher 对照 | 双侧P=.0038347022 | 概率排序定义；不填χ²/df |
| OR 与比例差 | OR=3.50，95%CI 1.502954231～8.150614137；RD=.133333333，95%CI .048988363～.217678304 | A相对B；log-Wald和独立比例Wald，z=1.96 |
| McNemar | 精确P=.0226558447；校正渐近P=.0247446720；未校正P=.0143058784 | b=18、c=6，各方法分开命名 |

实际产物为 `output/teaching/results.json`、`summary.csv`、`summary.txt`、`adverse_events_table.csv`、`diagnostics.png`、`diagnostic_points.csv`；参考输出由本次摘要同步。原始输入路径/哈希、版本、分析集、方向和方法标签在 JSON 中；运行产物不作为公共教学原始数据提交。

零边际/零样本组、孤立零格、稀疏正频数表、未知编码、配对重排/缺失/重复键、临界期望频数、未舍入`.050`分支、预设Welch遇不可定义Levene、界值越界后的动态说明均有实际测试。固定Welch不因Levene不可计算而停止；课程分流无法判断时仍须报错核查。零格或Tmin<5时，OR和RD的Wald区间均留空并标明当前实现未估计适当稀疏区间；不补造端点，不声称这个阈值适用于全部区间算法。

发布前独立复查发现并修正一处例题文字：`[[0,20],[4,16]]` 的 n=40、Tmin=2，按本课程链主要方法为 Yates（χ²=2.5，P=.1138462980），Fisher 双侧 P=.1060291060 仅作对照。实际脚本原已选 Yates；本次直接调用复算确认，未修改算法。

同轮复查还发现恒定比值 T=[2,4,6]、R=[1,2,3] 经对数相减会产生约10⁻¹⁶量级的舍入变异，绕过原有`SD==0`保护。现按对数数值尺度与机器精度判断不可分辨变异并拒绝该退化t分析；新增测试同时检查恒定比值被拒和接近1的可分辨小变异仍可分析。参考数据的复算结果不变。

PR后续独立复查再发现两个反例并修正：①两组各20个常数小数100.1和100.2，原预设Welch流程会把均值舍入噪声当方差；现先查观测范围是否为0，拒绝退化资料，并验证10⁻¹⁰量级可分辨变异未被固定容差误杀。②稀疏正频数表`[[1,2],[12,1]]`原来仍输出log-Wald OR区间；现保留OR点估计和具名Fisher结果，明确区间未估计。该修复针对稀疏近似不稳，不以不同算法的P与CI必须一致作为理由。

statsmodels 0.15.0 另在本地隔离依赖目录通过 `PYTHONPATH` 加载，实际运行 `mcnemar([[42,18],[6,54]], exact=True)` 及两种渐近参数，P值与表中三项一致。共享脚本使用SciPy `binomtest`，无需在默认环境导入statsmodels。此处仅比较这张表，不宣称不同实现的每个边界处理完全相同。

两个完整例题的 Python 读取块此前在 course/Welch 输出下联调通过；单样本无数据模板未执行。后续已实际生成并查看两组含量与完整配对对数差值的Q–Q图，标签、点数与布局可读，逐点数值可追到ID。图中存在中段和尾部偏离，配对图上端点偏离参考线；不能把图形读成“正态已证明”，也未据此声称任意教学/真实数据都满足t检验条件。学生须结合题设、异常值核查及样本量自己写判断。

诊断图使用中点绘图位置`(rank−0.5)/n`，横轴为标准正态分位数，参考线为样本均数加样本SD乘横轴值；没有r²或自动“通过”阈值。JSON保留`requires_human_review`和`automated_normality_decision=not_made`。两个新图形测试覆盖并列值、标识和值绑定，以及缺失整对/个别观测排除后的样本一致性；已有CLI测试扩展到6个产物。独立复查另在临时数据中打乱行序并加入缺失，实测各点ID和值、配对排除及产物保存正确。数值或图形均不能验证独立性。

八个边界案例另由两个不继承评审上下文的新任务代理单轮作答，八项达到选法/缺项/执行诚实边界；原始回复见 [转录](router-trial-transcript.md)。完整目录复制命令在隔离目录执行通过。均未据此宣称真实客户端自动触发、多轮分析或课堂效果已验证。

## 已定教学口径

- 含量：课程路线采用基于均值的 Levene，未舍入 P≤.05 选 Welch，否则选 pooled；另可事先选择固定 Welch 路线。比较方向 B−A，不按检验结果中较小的 P 挑策略。
- 不良事件：行按 A药、B药，列按发生、未发生；主要方法按课程独立四格表条件链选择，OR 表示 A 相对 B 的事件优势比，率差为 A−B。OR 与率差的 Wald 区间算法分别标明；其他算法不强求相同端点。
- 配对 Cmax：先按受试者键对齐，演示 ln(T)−ln(R)、GMR 及 90% CI 与 80%–125% 教学界值；`formal_be_assessment` 保持 `not_assessed`。该文件缺少序列、周期、AUC，不能作正式交叉 BE 判定。
- McNemar：课堂采用不一致对数 b+c<40 时精确二项；这是一项预定教学规则，不是普遍适用的数学分界。精确与渐近输出分别标示。

## R数值与文档模板：WebAssembly实跑

本轮无原生`Rscript`，另在隔离目录从npm官方包安装WebR 0.6.0，实际启动**R 4.6.0（2026-04-24），平台`wasm32-unknown-emscripten`**。只使用基础R及`stats`，不宣称验收了桌面安装、`car`包或SPSS。

已通过`source("maintainers/scripts/validate_teaching.R")`后调用`run_validation(c("output/github-diagnostic-verified/summary.csv", "output/R-validation"))`。脚本重新读取三份CSV，独立计算并比较**99个数值字段**，全部在预定容差内；包括均数/SD、Shapiro、Levene(mean)、pooled/Welch的t/df/P/CI、对数配对/GMR/90%CI、事件表/期望数/P/OR/RD区间及McNemar三法。Levene用绝对组内均值离差的一元ANOVA重建，不冒充`car::leveneTest`包实跑。

比较标准为`|R−Python| ≤ 绝对容差 + 相对容差×|Python|`；Shapiro用`1e-8 + 1e-7×|Python|`，其余用`1e-9 + 1e-8×|Python|`。本次最大绝对差约`2.504e-9`，来自Shapiro P值；不要求两种近似实现逐位相同。保留`r_results.csv`、`comparison.csv`及`sessionInfo.txt`。另把临时副本中一个Python P字段改成0.5，复核器如预期报1项失败并保存失败表；未改真实结果或原始输入。该反例确认比较器会拒绝不一致数据。

已提取SKILL及reference中的真实R代码块执行**20个案例**，覆盖普通两轨、n=2/n>5000的Shapiro状态、不可定义Levene、零单样本/零配对差、常数比值舍入、一条件恒定而配对差值可变、正常/稀疏/零格效应，以及精确McNemar与零不一致对子。修正了旧模板的NaN输出、诊断越界中断、Welch依赖Levene及稀疏区间未同步问题。测试使用临时输入副本，核对源CSV字节未变；报告与真实输出另存到`output/R-template-validation/`。

本地有Rscript的维护者可从仓库根目录复现下列命令；**本轮执行的是上述WebR函数入口，未实跑原生Rscript CLI**：

```bash
python maintainers/scripts/analyze_teaching.py --output-dir output/teaching --t-policy course
Rscript maintainers/scripts/validate_teaching.R output/teaching/summary.csv output/R-validation
Rscript maintainers/tests/test_R_templates.R
```

跨语言复核需先有Python摘要文件，这是维护者验收流程；学生选R轨无需安装Python，可直接运行R模板并保存自己的结果。99项只比较固定教学例的数值，不覆盖全部元数据、图形、客户端触发、正式BE或任意输入；20例也不证明一般鲁棒性。

## SPSS机房验收材料：生成完成，实机待运行

已实际执行`python maintainers/scripts/build_spss_check.py --output-dir output/spss-workstation-check`，生成可独立解压的ZIP：含一次性设置语法、四项任务语法、三份原始CSV的逐字节副本、Python重新计算的64条具名参考值、空白机房记录和SHA-256清单。四项任务分别为独立t、配对对数演示、独立四格表和精确McNemar复核；不含SPV/PDF或伪造截图。学生使用成包不需要Python/R。

实际测试确认输入副本/ZIP散列、参考值来源、所有实测值为空且状态为`not_run`，并确认已有目标目录或ZIP被拒绝覆盖。独立复核又补上点小数设置、把初始化纳入第一选区，并明确SPSS实跑须用全新解压目录，避免同名SPV被无提示覆盖。人工STOP注释不构成自动中断；本轮仅静态核对IBM命令资料，没有SPSS解析器或实机运行，不把64条参考值说成64项SPSS通过。操作步骤及版本/许可差异见[机房验收说明](spss-machine-check.md)。

## 共用Python分析的输出保护：实际复跑

独立审查在临时目录发现旧脚本以course、welch连续运行时均成功，却静默替换同一路径的六份输出。现于任何输出写入前创建全新目录；已有目录（包括空目录）、文件或链接占用该位置时拒绝保存并提示另选新目录，CLI返回非零状态。创建新目录后若写入中断，仍可能留下部分产物，须记“保存未完成”并在下次改用新目录；不把本改动写成六文件事务保存或所有软件通用保护。

新增两项回归测试已实际通过：重复运行不会改变第一轮六份产物及学生备注，另选目录的Welch可以完成，已有空目录也被拒绝；已有输出目录内的`summary.csv`链接指向临时输入CSV时，在任何输出写入前拒绝，输入字节和链接保持不变。完整28项测试通过，没有把未运行的SPSS算入。

已实际以course、welch分别保存到`output/output-guard-course/`和`output/output-guard-welch/`，各六份产物，输入哈希与现有CSV吻合。course的统计、图形数据五个根节与修复前留存结果逐项一致；本轮只改保存行为，未改统计算法。两项方法skill同步新目录及结果读取规则，并通过`quick_validate.py`。R代码未改，本轮未重新执行WebR/Rscript，既有R验收范围仍见前节。

另由未继承整改上下文的新任务代理按t-test技能说明执行两条事先指定策略，分别保存到两个新目录；两次退出码为0、stderr为空，第二轮后第一轮六份文件逐字节保持，三个输入CSV哈希不变。走查又校正了技能中笼统的`output/figures/`路径：共用Python脚本的图与其他结果都位于本轮指定目录根部。该试验只覆盖这两次Python文件流程，不等于R/SPSS、平台自动触发或真实课堂验收。

## 尚未执行或待核

课堂入口后续静态修订：限定作业增加课程软件、正课/课后AI范围、教材章节和提交要求的空白设置，以及教师试用记录。学生项目说明与决策模板同步允许“不用AI”的核查路径；没有新增统计方法、数值或学生日志，课程参与/卡点记录均未填写。此项仅为材料与流程核对，不构成真实课堂试用或教学效果证据。

| 项目 | 状态与要求 |
|---|---|
| 桌面R/Rscript及外部包 | 基础R已在WebR/R4.6.0完成99字段复算和20个模板案例；原生CLI、其他R版本、car及课堂安装仍待本机验收 |
| SPSS 25 以上实机 | 已提供可运行候选语法与64条空白验收记录；本轮无SPSS，语法、菜单、精确检验入口和实际输出须在课程机位核查，不能宣称跨版本默认值一致 |
| 国内教材口径 | 任课教师需填写所用人卫版《医学统计学》的具体版次、相关规则和本课取舍；本轮未取得可逐字核验的教材全文，不编页码或声称已完成教材一致性认证 |
| 真实课堂 | 尚未完成学生试用；自动数值测试、文档静态检查与模型任务试验均不能代替课堂验收 |
| 正式 BE | 未执行；须另行按适用规范和设计分析，当前数据不能通过补写虚构字段满足要求 |

## 依据与适用边界

- [SciPy Levene](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.levene.html)：mean 与 median 是不同中心定义；本仓库显式指定参数，避免软件默认值混用。
- [R Shapiro](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/shapiro.test.html)限定非缺失n为3～5000；当前模板不适用时记录`not_assessed`，不自动判断正态。[R t.test源码](https://svn.r-project.org/R/trunk/src/library/stats/R/t.test.R)及本次零差值实跑说明需要显式退化保护。
- [WebR 0.6.0文件系统](https://docs.r-wasm.org/webr/v0.6.0/mounting.html)与[下载说明](https://docs.r-wasm.org/webr/latest/downloading.html)支持Node中的R WebAssembly执行。本次隔离安装仅用于维护者验收，不新增学生的Node/WebR依赖。
- [SciPy 1.17 OR](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.stats.contingency.odds_ratio.html)：样本OR与条件最大似然OR及相应区间须分别命名。本最小脚本未添加稀疏精确区间实现，按明示范围留空。
- 图形使用[标准正态分布分位数](https://docs.scipy.org/doc/scipy-1.17.0/reference/generated/scipy.stats.norm.html)与[Matplotlib 3.10.8 Figure.savefig](https://matplotlib.org/3.10.8/api/_as_gen/matplotlib.figure.Figure.savefig.html)。绘图位置和参考线在代码及输出明确给出；未把SciPy `probplot`默认Filliben绘图位置冒称为本图算法。
- [R McNemar](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/mcnemar.test.html) 与 [statsmodels McNemar](https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html)：R 的 `mcnemar.test` 为渐近卡方实现；精确分支使用 `binom.test`，Python 显式设置 `exact`。
- [国家药监局 M13A 适用公告（2026年第49号，政府转载）](https://www.hunan.gov.cn/zqt/zcsd/202605/t20260521_33982465.html)与 [ICH M13A（FDA 发布的最终文本）](https://www.fda.gov/media/165049/download)：常规速释口服制剂 BE 有设计、参数及适用范围要求；80%–125% 不能无条件用于所有药物或设计。公告还规定既有方案的过渡安排，正式任务须按具体适用日期核查。
- [《中国药典》2025 年版四部增修订概况](https://www.cnpharm.com/c/2025-07-18/1076142.shtml)：旧 9011、9012 已删除，贡献指南不再以“2025 年版四部 9012”作现行引用示例。本例也不提供具体品种含量质量标准。
- 原生技能目录参照 [GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)、[Cursor](https://cursor.com/docs/skills)、[Claude Code](https://code.claude.com/docs/en/skills) 官方说明；仅核查目录格式，不等于在这些平台完成了实际安装与触发测试。
