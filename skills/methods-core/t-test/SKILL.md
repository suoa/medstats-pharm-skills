---
name: t-test
description: t 检验方法 skill（单样本、配对、两独立样本）。研究问题已指向1–2组计量结局的均数或均数差时使用，核查设计、正态性证据、异常值和分析集，执行课程指定的合并方差/Welch选择或事先预设的Welch。包含含量测定和对数尺度配对数据的教学演示、效应估计与区间报告；不据简化配对数据判定正式生物等效。严重偏离、重复测量、批次结构或目标不清时返回路由讨论，不自动把秩检验当均数检验的替代品。
---

# t 检验（t-test）

对 1–2 组计量资料的均数进行比较的参数方法。先利用 `method-selection-router` 的研究问题与设计记录，再在本 skill 核查方法前提；已有信息不重复询问。资料类型、实验单位或配对关系不清时返回路由，不能要求先用一次正态性检验“证明合格”才允许加载本文件。前提有争议时读[前提详解](references/assumptions.md)，执行教学例时读[例题与输出来源](references/examples.md)。

## 1. 何时用

| 类型 | 典型问法 | 数据结构 |
|---|---|---|
| 单样本 t | 这批片重是否等于标示值？实测均值是否与理论值不同？ | 一列观测值 + 一个已知标准 μ₀ |
| 配对 t | 同一批受试者服药前后？配成对子的两个样本？ | 根据设计按 ID / 对子号对齐，每行一对，先算差值 d |
| 两独立样本 t | 两个独立组的均数比较？ | 分组列 + 结局列；独立性须结合实验/抽样单位与设计确认 |

## 2. 何时不能用（前提与禁忌）

1. **结局不是计量资料**（有效/无效之类的二分类结局）→ 卡方或 Fisher，见 `chi-square`；
2. **明显偏态、极端离群或小样本下前提存疑** → 核查原始值、图形和目标量，必要时讨论变换或相应秩方法；n<30或Shapiro的P≤0.05都不是自动改法开关。秩方法不自动检验均数或中位数相等；相关 skill 尚未发布时可给一般指导，不声称已按仓库流程执行；
3. **三组及以上未经预设与多重性处理反复两两 t 检验** → 返回多组分析流程；`anova` 未发布时说明需教师核查，不假装调用；
4. **把配对数据当独立样本做**，或反之 → 核对题干/方案、实验或抽样单位、对象 ID、批次和测量次数。ID不重叠不能单独证明独立；
5. 两独立样本方差不齐时用合并方差 t → 改用 Welch t；
6. 独立样本要求组间独立、组内观测独立（不能把重复测量当独立样本）；
7. 离群值不得为了得到某个P值而删除；先查录入及实验记录，处理理由和必要的敏感性分析写入 DECISIONS.md；
8. 正式交叉试验、等效/非劣效、重复测量或整群/批次结构不直接套普通两组检验；本 skill 的简化配对演示不提供正式生物等效结论。

## 3. 执行步骤

### 3.0 通用准备

1. 从 `data/raw/` 读取原始数据，复制到 `data/clean/` 再处理；原始文件只读不改；
2. 核对数值、单位、实际样本量和缺失；本科默认不插补，记录纳入及排除数量。配对数据先核配对键及每条件记录唯一性，按键对齐后选完整对；不得分别去缺失再按行号拼接。重排某条件的记录后，匹配结果应不变；
3. 查看检验结果前，在 `DECISIONS.md` 一行记录本次规则、软件、主方法和方向；教师已指定的课程规则直接采用，不让学生维护配置。未指定时可预设 Welch，不按较小P值切换；
4. 核查环境能否读取、运行和保存；不能运行只给未执行指导，能计算但未保存时明确“已计算，尚未保存”，不得标作业文件验收通过。

### 3.1 单样本 t

- 计算 x̄、s、n；
- 前提：观测独立；结合Shapiro–Wilk、Q-Q图、异常值和样本量判断正态近似与方法稳健性。P>0.05不证明总体正态；
- 统计量 t = (x̄ − μ₀) / (s/√n)，df = n−1；
- 给出均数与 μ₀ 之差的 95% CI、Cohen's d（可选）。软件若给的是总体均数CI，须两端都减μ₀才是均数差CI，不能混用标签。

### 3.2 配对 t

- 逐对算差值 d = X₁ − X₂（**顺序必须固定并写明**，如 T−R 还是 R−T）；
- 检查对象是**差值的正态性**，不是两组原始数据各自正态；
- t = d̄ / (s_d/√n)，df = n−1；
- 给出差值均数的 95% CI；
- **对数尺度配对教学演示**：正值T、R参数分别取自然对数，计算ln(T)−ln(R)，再将差值均数及90%CI取指数得到GMR及区间。现有数据缺序列、周期和AUC，区间满足预设教学界值也不判正式BE。P>0.05不证明等效；区间未完全进入界值写“未能证明等效”，不能写“已证明不等效”。正式BE按适用指南和预设模型核查；专用 skill 未发布时不声称已执行。

### 3.3 两独立样本 t

1. 分组描述：n₁、x̄₁、s₁ 与 n₂、x̄₂、s₂；
2. 分别检查两组分布；配合Shapiro–Wilk和图形解释证据。小样本非拒绝可能是效能不足，大样本也可能检出轻微偏离；不靠固定30阈值或总n通关；
3. 执行事先记录的一套规则：
   - **课程路线**：按教师指定中心算法做Levene；本仓库教学例固定mean。未舍入P>0.05时按课程规则用合并方差t，df=n₁+n₂−2，并写“未发现方差不齐的证据”；P≤0.05用Welch，自由度由软件按Welch–Satterthwaite计算；
   - **通用路线**：预设Welch，不用Levene结果改变主要方法；不能据此改写教师指定的课程答案；
   - 软件只显示`.050`时提高精度，不能据显示值认定恰等于.05；仍无法判断则交教师核查。mean是经典Levene，median是常称Brown–Forsythe的变体；须明确版本与算法，不能假定各软件默认一致；
4. 给出均数差（写明谁减谁）及所选方法的95%CI；Cohen's d可选，并注明分母定义，不能将pooled CI配给Welch；
5. 输出写入 `output/`（表 + 文本结果），图写入 `output/figures/`。

### 3.4 收尾

- 在 LOG.md 记录一行：时间、数据文件、方法、关键结果文件路径；
- 报告中每个数字必须能在 `output/` 的结果文件中找到。

## 4. 软件执行（三轨）

单次作业选一轨，保持目标量、方向和算法一致；不同算法不要求数字相同。本次Python教学脚本有实跑验收；R/SPSS仅作官方文档与静态核对，尚未实跑，不宣称三轨验证通过。以下代码是输入已清理的最小模板，完整教学脚本与保存方式见[例题](references/examples.md)。

### 轨 A：SPSS（菜单路径）

- 单样本：`分析 → 比较平均值 → 单样本 T 检验`，检验值填 μ₀；
- 独立样本：`分析 → 比较平均值 → 独立样本 T 检验`；定义组值并写清“组1−组2”。按已选课程规则或预设Welch读对应行，不按较小P选行；新版本可能需另选方差齐性输出，核对实际表头与中心算法；
- 配对样本：`分析 → 比较平均值 → 配对样本 T 检验`，选入成对变量；
- 正态性：`分析 → 描述统计 → 探索`，绘图勾选"含检验的正态图"（输出 Shapiro–Wilk）。
- 配对先用`转换 → 计算变量`计算差值；对数演示先核T/R均为正，再计算LN(T)、LN(R)及其差值。保存菜单“粘贴”生成的`.sps`、实际`.spv`和含表名的PDF导出，允许准确转录并标表名/行列。菜单参照SPSS30中文文档；不同版本的“比较平均值/比较平均数和比例”“配对/成对”名称可能不同，按机房实际界面核对。

### 轨 B：R

```r
# Templates: provide cleaned x, mu0, a, b and ID-aligned pre/post first.
t.test(x, mu = mu0)
t.test(dat$post, dat$pre, paired = TRUE)
levdat <- data.frame(value = c(a, b),
  group = factor(rep(c("A", "B"), c(length(a), length(b)))))
lev <- car::leveneTest(value ~ group, data = levdat, center = mean)
policy <- "course"  # Set before examining results; alternatively "welch".
stopifnot(policy %in% c("course", "welch"))
use_pooled <- policy == "course" && lev[["Pr(>F)"]][1] > 0.05
fit <- t.test(b, a, var.equal = use_pooled, conf.level = 0.95)
dir.create("output", recursive = TRUE, showWarnings = FALSE)
write.csv(data.frame(direction = "B - A", method = fit$method,
  t = unname(fit$statistic), df = unname(fit$parameter), p = fit$p.value,
  mean_diff = mean(b) - mean(a), ci_low = fit$conf.int[1], ci_high = fit$conf.int[2]),
  "output/t_result.csv", row.names = FALSE)
capture.output(list(shapiro_A = shapiro.test(a), shapiro_B = shapiro.test(b),
  levene = lev, test = fit, versions = sessionInfo()), file = "output/t_run.txt")
```

### 轨 C：Python（SciPy，脚本产物可复跑）

```python
from scipy import stats
# Templates: provide cleaned x, mu0, a, b and ID-aligned x_t/x_r first.
stats.ttest_1samp(x, popmean=mu0)
stats.ttest_rel(x_t, x_r)
policy = "course"  # Set before examining results; alternatively "welch".
assert policy in {"course", "welch"}
lev = stats.levene(a, b, center="mean")
use_pooled = policy == "course" and lev.pvalue > 0.05
fit = stats.ttest_ind(b, a, equal_var=use_pooled)
ci = fit.confidence_interval(confidence_level=0.95)
stats.shapiro(a)  # At least 3 observations; not a pass/fail certificate.
```

运行下列命令保存两份完整教学例的效应、CI、方向、版本和输出来源；本命令默认从现有CSV分析，不重新生成原始数据：

```bash
python scripts/analyze_teaching.py --output-dir output/teaching --t-policy course
```

在仓库根目录运行；结果见`output/teaching/results.json`、`summary.csv`与`summary.txt`。若事先指定通用Welch路线，将参数改为`--t-policy welch`，报告相应CI。调用失败时保留真实错误，不补写参考数字冒充输出。

## 5. 结果报告模板

- **单样本**：n=＿，x̄±s=＿±＿（单位），与题目给定μ₀=＿比较，t(df)=＿，P=＿；均数差x̄−μ₀=＿，95%CI（＿，＿）。μ₀须有题干或规范来源。
- **配对**：服药后与服药前比较，差值 d̄=＿（95%CI：＿～＿），t(＿)=＿，P=＿，可认为服药前后差异有/无统计学意义。
- **独立样本**：A组n=＿、x̄±s=＿±＿，B组n=＿、x̄±s=＿±＿；按预设＿路线采用＿t检验，t(df)=＿，P=＿；均数差（B−A）=＿，该方法95%CI（＿，＿）。课程路线另报Levene中心算法与P，d按要求选报并写分母定义。

书写纪律：
- 先给描述统计（n、x̄±s），再给检验结果，最后给效应量与专业解释；
- P是在H₀及模型假设下出现当前或更极端统计结果的概率，不是H₀为真的概率。按预设α写“差异有/无统计学意义”；给确切P，P<0.001时可写P<0.001，不写“高度显著”；
- 无论P是否达阈值均报告效应和区间；95%CI描述估计不确定性，不能解释为本次固定参数有95%概率在区间内。SD描述个体离散，标准误描述估计精度；
- 缺少专业重要差异界值或明确品种标准时，写“尚不能判断专业重要性/合格性”，不得凭均数或P值补出结论；
- 每个数字注明本次输出文件及字段或表名。软件未运行不写“已验证”；能计算未保存如实记状态。手算可作有标记的复核，不替代软件主结果来源。

## 6. 验证清单

- [ ] 实验/抽样单位、独立或配对关系有题干/方案与数据共同支持，未将批次或重复测量当独立重复
- [ ] 配对键及唯一性已查，按键对齐后处理完整对；重排记录不改变结果，实际纳入与缺失对数已记
- [ ] 单样本给出 μ₀ 来源；配对差值方向写明
- [ ] 正态性证据及图形已结合解释，配对检查差值；没有用P>0.05或固定n证明前提成立
- [ ] 课程/预设Welch规则已事先记明；课程路线明确Levene中心及未舍入P分支，不按显示`.050`猜选行
- [ ] 报告均数差与对应方法CI；d可选，定义明确；对数演示的90%CI不混作一般95%CI
- [ ] 未对3组及以上未经预设及多重性处理反复两两检验；未伪称调用未发布skill
- [ ] 报告数字全部来自 output/ 结果文件；DECISIONS.md、LOG.md 已更新
- [ ] 已区分统计学意义与专业意义
- [ ] 对数配对例仅报告教学区间条件，`formal_be_assessment`保持`not_assessed`；未作正式BE或药典合格判定
