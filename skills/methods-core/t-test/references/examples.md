# t 检验例题（references/examples）

例题 1、2 使用本仓库 `datasets/teaching/` 中的**教学模拟数据**；例题 3 只是待填输入的单样本模板。每页代码都可直接运行、读得懂；参考数字是我们对已落盘 CSV 的复算，供你核对自己的输出，**不能照抄成"我的运行结果"**。数据生成与学生分析是两件事：不要为了凑答案去重建数据，直接读仓库里的 CSV。

运行前先建好输出目录（代码里会往 `output/` 写文件）：

```bash
mkdir -p output
```

三轨实跑状态：Python 代码已在仓库当前环境实跑；基础 R 模板在 WebR/R 4.6.0 做过数值复核；桌面 R 与 SPSS 尚未在本机验证。三轨可选不等于三轨都已验证。

---

## 例题 1：独立样本 t —— 两种制片工艺含量测定

数据：`datasets/teaching/tablet_assay.csv`（A 对照工艺、B 新工艺各 20 片，含量相当于标示量 %）。

### 路由

结局 assay_pct 是计量资料（标示量百分比），目标是 B−A 的均数差。**本题预设各片观测独立**，采用课程路线（经典 Levene，中心 mean；未舍入 P>0.05 读合并方差 t）。ID 不重叠本身不能证明真实工艺重复独立：真实研究要核对每工艺批次数和抽样单位，每工艺仅一批而抽多片时不能据此推广工艺效果。

### Python：读 CSV、检查、检验、保存结果

```python
import os
import pandas as pd
from scipy import stats

os.makedirs("output", exist_ok=True)
df = pd.read_csv("datasets/teaching/tablet_assay.csv")
a = df.loc[df.process == "A_对照工艺", "assay_pct"]
b = df.loc[df.process == "B_新工艺", "assay_pct"]
print(len(a), len(b), a.describe(), b.describe())

# 前提：两组各自的分布（Shapiro 非拒绝不证明正态，还要看 Q-Q 图和异常值）
print(stats.shapiro(a))                 # W=0.955, P=0.449
print(stats.shapiro(b))                 # W=0.942, P=0.264

# 课程路线：经典 Levene（SciPy 默认 center="median"，必须显式改成 "mean"）
lev = stats.levene(a, b, center="mean")
print(lev)                              # F=0.739, P=0.395

# 用未舍入的 P 决定读哪一行，不能看屏幕上显示的 .050 猜
use_pooled = lev.pvalue > 0.05
fit = stats.ttest_ind(b, a, equal_var=use_pooled)   # 方向固定 B − A
ci = fit.confidence_interval(0.95)
print(fit.statistic, fit.df, fit.pvalue, ci)

# 可选效应量：Cohen's d，分母写清楚（这里用合并 SD）
sp = (((len(a)-1)*a.var(ddof=1) + (len(b)-1)*b.var(ddof=1))
      / (len(a)+len(b)-2)) ** 0.5
d = (b.mean() - a.mean()) / sp

# 把本次结果存盘，报告数字以这个文件为准
pd.DataFrame([{
    "direction": "B-A", "method": "pooled" if use_pooled else "welch",
    "t": fit.statistic, "df": fit.df, "p": fit.pvalue,
    "mean_diff": b.mean()-a.mean(),
    "ci_low": ci.low, "ci_high": ci.high, "cohens_d": d
}]).to_csv("output/tablet_t_result.csv", index=False)
```

若教师事先指定通用 Welch 路线，则不做 Levene 分流，直接 `equal_var=False`，并且 CI 也要读 Welch 的，不能配 pooled CI。本例两组 n 相等，两种 t 的数值恰好相同，这不是一般规律。

### 结果（参考答案）

| 组别 | n | x̄（%） | s（%） |
|---|---|---|---|
| A 对照工艺 | 20 | 98.497 | 0.958 |
| B 新工艺 | 20 | 99.257 | 1.093 |

- Shapiro–Wilk：A 组 W=0.955、P=0.449，B 组 W=0.942、P=0.264；未发现足以拒绝正态性的证据，仍须看 Q-Q 图与异常值，不能仅凭这两个 P 宣布正态；
- Levene(mean)：F=0.739、P=0.395；未发现方差不齐的证据，按本题课程规则读合并方差 t；
- **t(38)=2.338，P=0.025**；均数差 B−A=0.760 个百分点，95%CI（0.102，1.418），Cohen's d=0.739（合并 SD 为分母）。
- 若以 Welch 为主要分析：t=2.338、df=37.36、P=0.025，95%CI（0.101，1.419）；不能把 pooled 的 CI 挪给 Welch。

### 报告示范

> 在独立观测的教学假设下，对照工艺组含量为 98.50%±0.96%（n=20），新工艺组为 99.26%±1.09%（n=20）。Shapiro–Wilk 未发现足以拒绝正态性的证据（P 均>0.05），分布形态仍需结合图形核查。Levene(mean) 检验 F=0.739、P=0.395，按预设课程路线采用合并方差 t 检验，t(38)=2.338，P=0.025；B−A 均数差为 0.76 个百分点，95%CI 为 0.10～1.42。结果达到预设 α=0.05 的统计学阈值；本题没有给定具体品种的专业重要差异界值或质量标准，**尚不能据此判断专业重要性或药典合格性**。

95.0%–105.0% 若用于课堂讨论，只能称"本情境预设的示意范围"，不是通用药典限度；均数比较也不替代品种放行或逐片质量判断。P 值是在 H₀ 及模型假设下出现当前或更极端结果的概率，不是"差异由随机造成的概率"，也不衡量效应重要性。

### R 版（同题，直白写法）

```r
df <- read.csv("datasets/teaching/tablet_assay.csv")
a <- df$assay_pct[df$process == "A_对照工艺"]
b <- df$assay_pct[df$process == "B_新工艺"]
shapiro.test(a); shapiro.test(b)

# 基础 stats 实现 mean 中心 Levene：对组内绝对离差做单因素方差分析，无需 car 包
dev <- data.frame(e = c(abs(a-mean(a)), abs(b-mean(b))),
                  g = factor(rep(c("A","B"), c(length(a), length(b)))))
oneway.test(e ~ g, data = dev, var.equal = TRUE)

fit <- t.test(b, a, var.equal = TRUE)   # P=0.395>0.05，课程路线读合并方差
fit

# 保存结果（数字来自输出，不手打）；Cohen d 在 R 里可另用效应量包或手算
dir.create("output", showWarnings = FALSE)
write.csv(data.frame(t = unname(fit$statistic), df = unname(fit$parameter),
                     p = fit$p.value, mean_diff = unname(diff(fit$estimate)),
                     ci_low = fit$conf.int[1], ci_high = fit$conf.int[2]),
          "output/t_independent_result.csv", row.names = FALSE)
```

注：`diff(fit$estimate)` 给出的是 B 组均值减 A 组均值（t.test 输出顺序为 mean of x, mean of y，此处 x=b、y=a）。

### SPSS 读图提示

独立样本检验输出有"假设等方差"（合并方差）与"不假设等方差"（Welch）两行；本题 Levene P=0.395，读第一行。若预设 Welch 则固定读第二行，不得比较两行后挑 P 小的。显示 P=.050 时提高显示精度再判。SPSS 本例尚未在机房实机验证。

---

## 例题 2：配对 t（对数尺度）—— 等效界值教学演示

数据：`datasets/teaching/bioeq_cmax.csv`（24 个示意对象，`subject_id`、`cmax_T`、`cmax_R`，单位 ng/mL）。文件名为历史命名；现有列**不含 sequence、period 或 AUC，不能当作完整双周期双交叉 BE 数据**。先按 ID 确认唯一对象、完整对和正值。

### 为什么先取对数

浓度数据常见右偏；本例对正值 T、R 取自然对数，演示差值与比值的换算。检查的是 ln(T)−ln(R) 的分布，不能假定取对数后必然正态。预设教学界值为 80.00%–125.00%；ln(0.8) 与 ln(1.25) 关于 0 对称。本例用 90%CI 演示区间条件，不把这条规则无条件推广到特殊品种或复杂 BE 设计。

### Python：读 CSV、按 ID 对齐、检验与换算

```python
import os
import numpy as np, pandas as pd
from scipy import stats

os.makedirs("output", exist_ok=True)
df = pd.read_csv("datasets/teaching/bioeq_cmax.csv")
assert df.subject_id.is_unique and (df.cmax_T > 0).all() and (df.cmax_R > 0).all()
ln_t, ln_r = np.log(df.cmax_T), np.log(df.cmax_R)
d = ln_t - ln_r                          # 配对差值，方向固定 ln(T)−ln(R)
print(stats.shapiro(d))                  # 检查的是差值：W=0.971, P=0.682
fit = stats.ttest_rel(ln_t, ln_r)
print(fit.statistic, fit.df, fit.pvalue) # t=-0.624, df=23, P=0.539

# GMR 与 90%CI：差值均数 m 及其标准误，区间端点取指数后乘 100
n = len(df)
m = d.mean()
se = d.std(ddof=1) / np.sqrt(n)
tc = stats.t.ppf(0.95, n - 1)            # 90%CI 用双侧各 5%
gmr = np.exp(m) * 100
ci_low, ci_high = np.exp(m - tc*se)*100, np.exp(m + tc*se)*100
print(f"GMR={gmr:.2f}%  90%CI=({ci_low:.2f}%, {ci_high:.2f}%)")

pd.DataFrame([{"direction": "ln(T)-ln(R)", "t": fit.statistic, "df": fit.df,
               "p": fit.pvalue, "gmr_pct": gmr,
               "ci90_low": ci_low, "ci90_high": ci_high,
               "interval_criterion_met": ci_low >= 80 and ci_high <= 125,
               "formal_be_assessment": "not_assessed"}]
             ).to_csv("output/bioeq_paired_result.csv", index=False)
```

GMR 是各配对 T/R 比值的几何均值，不能用原尺度算术均数之比代替。差值均数的 95%CI 与 GMR 的 90%CI 是两件事，不能互换。

### 结果（参考答案）

- 差值 Shapiro–Wilk W=0.971、P=0.682；仅表示未发现足以拒绝正态性的证据，图形与异常值仍应核查；
- 配对 t：**t(23)=−0.624，P=0.539**；
- GMR=98.10%，**90%CI（93.06%，103.41%）**；在简化配对教学模型中区间完全进入预设界值，区间条件成立；
- **正式 BE 评价状态：未评估（not_assessed）**——无论教学区间条件是否成立，都不能凭这份缺序列、周期和 AUC 的数据作正式 BE 结论。

### 关键反直觉点（必讲）

P=0.539 只表示在所用模型下未拒绝"总体平均对数差为 0"，不证明 T、R 相同或等效。若 90%CI 很宽（例如 70%–140%），同样可能 P>0.05，却明显不满足界值，此时应写"未能证明等效"，不能写"已证明不等效"。正式 BE 还要按适用指南、预设设计/统计模型及所需 PK 参数评价。

### 报告示范（简化教学模型）

> 对 24 个示意对象的 T、R 正值取自然对数后作配对分析，差异检验 t(23)=−0.624、P=0.539。简化模型的 T/R 几何均值比为 98.10%，90%CI 为 93.06%～103.41%，满足预设 80.00%～125.00% 的教学区间条件。数据缺序列、周期和 AUC，未作正式制剂 BE 评价。

SPSS 指导（未实跑）：按 ID 确认完整对后，用"转换 → 计算变量"算 LN(T)、LN(R) 与对数差；正态性检查对数差。做本区间演示时把配对分析的置信度设为 90%，确认差值方向为 LN(T)−LN(R)，再对端点取指数乘 100；不要把默认 95% 输出误读为 90%。保存计算变量语法和结果来源。

---

## 例题 3：单样本 t —— 片重与标示值（模板）

单样本没有配套数据，给最小模板：

```python
from scipy import stats
# 20 片片重(mg)，标示平均片重 100 mg
t, p = stats.ttest_1samp(weights, popmean=100)
```

R：`t.test(weights, mu = 100)`。

报告："片重 x̄±s=＿±＿mg（n=20），与题目给定值 100 mg 比较，t(19)=＿，P=＿；均数差 x̄−100=＿mg，均数差 95%CI（＿，＿）。"软件若给的是总体均数 CI，报告差值 CI 需两端各减 100 mg。本模板尚无 `weights` 数据、没有实际运行，不计为完整可复跑例题。另注意药典片剂重量差异检查有专属的计数式判定规则（超限片数），不是 t 检验，不要混用。
