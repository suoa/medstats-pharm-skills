---
name: chi-square
description: 比较独立组分类结局的率或完整构成，或比较两个相关二分类结果的边缘率时使用。新问题先经 method-selection-router；已留痕的同一分析可直接进入。覆盖独立2×2的课程选法链、R×C Pearson、Fisher双侧和精确McNemar，核对事件编码、行列方向、期望频数、效应与区间。等级结局若比较整体高低，转秩方法或有序模型；若比较完整类别构成，可用列联表但说明未利用次序。调整混杂、整群或三个以上相关时点不在本流程内。
---

# χ² 检验（chi-square）

先确认研究问题、抽样或实验单位以及独立/相关结构。ID不重叠不能单独证明观测独立；已有题干与设计说明直接采用，不要求学生重复填写。规则未指定时先确定本次主要选法并留痕，不根据较小P值换方法。

## 1. 何时用

| 设计与研究问题 | 表型 | 候选方法 |
|---|---|---|
| 两独立组，比较二分类发生比例 | 2×2 | 按本次课程规则选择未校正Pearson / Yates / Fisher双侧 |
| 独立组，比较多类别完整构成 | R×C | Pearson；稀疏时另核精确或模拟方法 |
| 同一对象两个时点/两种方法，比较二分类边缘率 | 配对2×2 | McNemar；小样本课程路线用精确二项法 |
| 有序结局，研究整体等级高低 | 有序类别 | 返回Router，候选秩方法或有序模型 |

含量百分数等连续测量不是二分类发生率；不能仅因带“%”就进入本skill。多组剂量的趋势检验与任意构成差异是不同问题，先回Router明确目的。

## 2. 何时不能用（前提与禁忌）

1. 不能把相关、重复或整群观测当作独立病例；三个以上相关时点、中心/批次聚集或需要控制年龄性别时，返回设计或调整分析分支。
2. 等级资料可比较完整构成，但普通χ²不利用类别顺序；不能把该结果解释为总体等级更高。连续资料按事后切点分组会损失信息；已有临床阈值的二分类问题须预先说明。
3. 只有百分数、没有实际分子分母时暂停检验，不虚构频数；不能把“事件病例中A药占比”当成A药发生率。
4. R×C总体检验不能推出任意两组均不同；事后比较须定义比较对象和比较族，并调整多重比较。不能只挑P较小的分割表。
5. 检验关联不能直接证明因果；病例对照抽样不能据组内病例比例估计人群发生风险。OR不能直接解读为风险比。
6. 先排查退化表、未知编码及缺失，再决定是否检验；零格处理见§3.1，不能静默加0.5或删类别凑条件。

## 3. 执行步骤

### 3.1 核对输入，固定方向，再计算期望频数

- 个体数据保留原始记录；合法汇总频数数据保留来源、分母和原始表，不伪造个体记录。频数须为非负整数，不能把百分比当人数。
- 对本例先确认分组只含A药/B药、事件只含0/1；先处理并记录缺失，再重排。遇未知类别先报错，不能用重排静默丢弃。固定**行[A药,B药]，列[发生1,未发生0]**；OR与RD均为A相对B。
- 期望频数 T_rc = n_r+ × n_+c / n。先检查总数与行列合计；任一行/列合计为0，标为退化表。本轮教学流程只描述可定义的频数和率，不运行Pearson/Yates或Wald OR区间；样本量为0的组发生率写“不适用”。
- 观察零格而边际均正不等于零期望频数；可按生效规则做Fisher。OR可能为0或无穷；未实现适当稀疏区间时写“未估计该区间”及原因，不补造端点。

### 3.2 独立2×2：本仓库课程选法链

以下是本次课程约定，**仅适用于独立两组二分类，且已排除退化表**；它不是所有软件的默认算法，也不是普遍定理。任课教师指定教材的书名、版次及原文尚待核对，不补写页码。

1. n<40 或最小期望频数Tmin<1 → Fisher双侧；
2. 否则，Tmin<5 → Yates连续性校正χ²；
3. 否则 → 未校正Pearsonχ²。

查看结果前记录主要方法。可同时输出其他方法作算法对照，须分别命名，不能按最小P值改结论。Fisher双侧以固定边际的超几何分布为基础，常用R/SciPy定义累加概率不大于观测表概率的表；**一般不等于单侧P乘2**。

### 3.3 R×C：比较完整类别构成

- 本课程的渐近条件约定：T<5的格子不超过总格子的20%，且无T<1。不得机械套用2×2的n=40分界；df=(R−1)(C−1)。
- 不满足时，可考虑专业上有依据且事先确定的类别合并，或适当的R×C精确/Monte Carlo方法；不能为得到显著结果合并类别。当前Python教学脚本只实现指定2×2例题，不声称已实现R×C精确流程。
- 总体拒绝H₀只说明至少存在构成差异；两两比较另定方案及校正。一般R×C表没有一个通用OR。

### 3.4 配对2×2：McNemar

| | B阳性 | B阴性 |
|---|---|---|
| A阳性 | a（一致） | b |
| A阴性 | c | d（一致） |

- 原始配对数据先核对配对键、每条件下记录唯一性，按键对齐，再选择完整对；不得分别去缺失后按行号拼接。保存纳入/排除对数，重排一条件记录不应改变结果。
- H₀是两类不一致结果的总体概率相同；检验只使用b、c。a、d仍用于样本量、边缘率与描述。
- m=b+c=0：单独说明没有不一致对子，本轮流程不运行检验，不套除法公式，也不解释为已证明等效。
- 本课程：m<40用双侧精确二项检验 X~Binomial(m,0.5)；m≥40用未校正渐近χ²=(b−c)²/m。精确法也可预先用于更大的m，40是课程分界。
- 连续性校正渐近法可作具名对照，不能把其P值称为精确P；不声称SPSS所有版本/过程都自动采用本课程分界。

### 3.5 效应与置信区间：不依赖显著性

- 无论P是否达到阈值，均报告与设计和问题对应的实际频数、分母、率及预设效应。
- 独立2×2：RD=pA−pB；样本OR=ad/bc。说明方向和CI算法。本例采用RD的Wald区间、样本OR的log-Wald区间；稀疏或边界比例时不能无条件套用这些近似。
- R `fisher.test`的OR是条件最大似然估计，CI为条件精确区间；与交叉乘积OR/log-Wald CI不是同一算法，分别命名，不要求端点相同。
- 配对数据可报告两边缘率及其差，不能套用独立率差的标准误。尚未实现合适配对区间时明确注明，不强填独立区间。McNemar不衡量一致性。

### 3.6 保存与溯源

保存带行列标签的表、期望频数、主要方法、比较方向、P值类型和效应/CI算法。报告每个数字须能追溯到本次实际输出；不以参考答案替代运行。DECISIONS记规则与一句理由，LOG记运行及产物路径，复用已有信息。

## 4. 软件执行（三轨，单份作业选一轨）

### 轨A：SPSS（菜单与语法需在本机核对；本次未实跑）

- 汇总频数输入：`数据 → 加权个案`，按频数变量加权；先核对频数总数。个体数据先确认没有遗留加权。更换任务后核对并按需要关闭加权。
- `分析 → 描述统计 → 交叉表`，行放分组、列放结局；“统计”选卡方，独立2×2可选风险；“单元格”选观测、期望和行百分比。
- 原始事件编码0=未发生、1=发生时，默认升序会把未发生放第一列。保留原变量，另建显示码1=发生、2=未发生，并检查实际行列标签；不能把反方向OR写成A相对B发生事件的OR。
- 按总数和期望频数执行本次课程链，再读取对应Pearson、连续性校正或Fisher双侧行/列。McNemar勾选对应统计项，检查实际“精确/渐近”“双侧”列名及脚注，不假定自动算法。
- 菜单用“粘贴”保留.sps，保存.spv及可读PDF导出。允许准确转录并写明表名/行列；未输出的RD CI须用另经验证的过程计算，不能从答案补数。

### 轨B：R（已在WebR执行；桌面环境仍须核对）

```r
dat <- read.csv("datasets/teaching/adverse_events.csv", check.names = FALSE)
stopifnot(all(c("drug", "adverse_event") %in% names(dat)))
if (anyNA(dat[c("drug", "adverse_event")])) stop("先记录并处理缺失")
if (!all(dat$drug %in% c("A药", "B药")) ||
    !all(dat$adverse_event %in% c(0, 1))) stop("未知分组或事件编码")
tab <- table(drug = factor(dat$drug, levels = c("A药", "B药")),
             event = factor(dat$adverse_event, levels = c(1, 0)))
dir.create("output/chi_square_R", recursive = TRUE, showWarnings = FALSE)
write.csv(as.data.frame.matrix(tab), "output/chi_square_R/table.csv")
rates <- ifelse(rowSums(tab) > 0, tab[, 1] / rowSums(tab), NA_real_)
capture.output(tab, rates, sessionInfo(), file = "output/chi_square_R/description.txt")
if (any(rowSums(tab) == 0) || any(colSums(tab) == 0)) {
  stop("退化表：已保存描述；NA表示分母为0，不运行检验")
}
expected <- outer(rowSums(tab), colSums(tab)) / sum(tab)
primary <- if (sum(tab) < 40 || min(expected) < 1) {
  fisher.test(tab, alternative = "two.sided")
} else {
  chisq.test(tab, correct = min(expected) < 5)
}
# Fisher条件OR/精确CI与样本OR/Wald CI分别命名；完整效应输出见例题。
capture.output(tab, expected, primary, sessionInfo(),
               file = "output/chi_square_R/test.txt")

# 已核对的配对频数示例；原始配对数据须先按键对齐。
b <- 18L; c <- 6L; m <- b + c
if (m == 0) {
  message("无不一致对子：本流程不运行检验")
} else {
  exact <- binom.test(b, m, p = 0.5, alternative = "two.sided")
  capture.output(exact, file = "output/chi_square_R/mcnemar_exact.txt")
}
```

### 轨C：Python（pandas + SciPy/statsmodels）

核心就三步：按"事件优先"固定列序 → 查期望频数按课程链选法 → 报效应与区间。完整可运行代码、效应量手算与课堂变式见[例题](references/examples.md)。

```python
import pandas as pd
from scipy import stats

df = pd.read_csv("datasets/teaching/adverse_events.csv")
# 关键：crosstab 默认列按 0,1 排，会让 OR 方向反过来。显式 reindex 固定
# 行[A药,B药]、列[发生1,未发生0]，OR/RD 均为 A 相对 B。
tab = pd.crosstab(df["drug"], df["adverse_event"]).reindex(
    index=["A药", "B药"], columns=[1, 0], fill_value=0)

chi2, p, dof, expected = stats.chi2_contingency(tab, correction=False)
print(tab, expected, chi2, dof, p)
odds, p_f = stats.fisher_exact(tab)   # 注意 odds 的方向与表的列序绑定
# McNemar（配对表 [[a,b],[c,d]]，b+c<40 用精确法）：
from statsmodels.stats.contingency_tables import mcnemar
print(mcnemar([[a, b], [c, d]], exact=True))
```

各轨实跑范围以仓库验证记录为准；R 的 WebAssembly 复核不能改写成桌面 R 与 SPSS 均已通过。

## 5. 结果报告模板

- **独立2×2，Pearson/Yates**：A组＿/＿（＿%），B组＿/＿（＿%）；n=＿，Tmin=＿。按本次课程规则采用＿χ²，χ²(1)=＿，P=＿；A相对B的样本OR=＿（log-Wald95%CI＿），RD=＿个百分点（Wald95%CI＿）。
- **Fisher**：各组频数/分母与率为＿；按预设规则采用Fisher双侧精确检验，P=＿。效应估计及CI算法为＿；未估计的区间说明原因。**不填Pearsonχ²或df。**
- **R×C**：报告完整类别分布；Pearsonχ²(df)=＿，P=＿。结论按实际结果写存在/未发现构成差异；若实施两两比较，另列比较对象与多重校正。
- **配对**：完整对n=＿；A、B阳性率分别＿、＿，b=＿、c=＿。采用McNemar双侧精确二项法，P=＿；或具名报告预设渐近χ²及df。精确法不强填χ²/df；无不一致对子单独描述。

P给足以判断阈值的精度，不写P=0.000；P<0.001时可写P<0.001。P是在H₀及模型假设下得到当前或更极端结果的概率，不是H₀为真的概率。CI描述估计精度与不确定性；不能凭P>0.05声称相同/等效。观察数据只报告关联；缺专业判定标准时不强行判断药学重要性。

## 6. 验证清单

- [ ] 研究问题与独立/相关结构有设计依据；等级构成与等级高低已区分
- [ ] 实际分子分母、事件编码、未知值和缺失已核对；汇总输入保留来源并正确加权
- [ ] 固定并保存行列标签与方向；没有重排后静默丢类别
- [ ] 退化表、观察零格与零期望频数已区分，零组分母不写0%
- [ ] 本次课程规则预先记录；2×2、R×C与McNemar使用各自条件，未按较小P选法
- [ ] 原始配对记录按键唯一对齐、完整对处理正确；无不一致对子单独说明
- [ ] Fisher/McNemar的精确或渐近、双侧、校正与否准确；没有强填χ²/df
- [ ] 效应及CI不依赖显著性；OR方向与估计/CI算法明示，配对未套独立区间
- [ ] 总体R×C结论没有扩成每两组均不同；多重比较另有方案
- [ ] 数字来自本次真实产物，日志可追溯；未运行或未保存的状态如实标明
