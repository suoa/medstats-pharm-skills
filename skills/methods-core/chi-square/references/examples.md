# χ² 检验例题（references/examples）

例 1 使用 `datasets/teaching/adverse_events.csv` 的教学模拟数据；例 2 是课堂构造的配对频数；末尾是一组课堂变式。所有 Python 代码都可直接运行，参考数字由我们对已落盘 CSV 实算得到，供核对，不能当作你自己的运行结果照抄。R 代码在 WebR/R 4.6.0 执行过；桌面 R 与 SPSS 仍须在所用环境核对后再标通过。

运行前先建输出目录：`mkdir -p output`。

---

## 例题 1：两独立组不良事件发生率

A 药、B 药各 120 例；adverse_event 为 1=发生、0=未发生。按本题教学假设病例间独立；真实数据还要核对中心、批次和重复记录等设计信息，不能仅从 ID 判断独立。

### 路由与主要规则

研究问题是两个独立组的二分类发生率是否不同。先核对分子分母和编码，再固定**行[A药,B药]、列[发生1,未发生0]**。本次课程链：n<40 或 Tmin<1 用 Fisher 双侧，否则 Tmin<5 用 Yates，其余用未校正 Pearson。此链是课程约定，不是所有教材的普遍定理，任课教师指定教材的原文仍待核。

### Python 全过程：固定方向、选法、算效应、存结果

```python
import os
import pandas as pd
from scipy import stats

os.makedirs("output", exist_ok=True)
df = pd.read_csv("datasets/teaching/adverse_events.csv")

# —— 输入核查 ——
assert set(["drug", "adverse_event"]).issubset(df.columns)
assert not df[["drug", "adverse_event"]].isna().any().any()
assert df["drug"].isin(["A药", "B药"]).all()       # 未知分组不许静默丢弃
assert df["adverse_event"].isin([0, 1]).all()

# —— 固定方向（最容易出错的一步）——
# pd.crosstab 默认列按 0,1 升序排列，会把 OR 方向弄反；
# 必须显式 reindex：行 A药/B药，列 发生1/未发生0。
tab = pd.crosstab(df["drug"], df["adverse_event"]).reindex(
    index=["A药", "B药"], columns=[1, 0], fill_value=0)
print(tab)
# adverse_event   1    0
# drug
# A药            24   96
# B药             8  112

# —— 期望频数与课程选法链 ——
chi2, p_pearson, dof, expected = stats.chi2_contingency(tab, correction=False)
chi2_y, p_yates, _, _ = stats.chi2_contingency(tab, correction=True)
odds_f, p_fisher = stats.fisher_exact(tab, alternative="two-sided")
n, tmin = tab.to_numpy().sum(), expected.min()
if n < 40 or tmin < 1:
    primary = "Fisher 双侧"
elif tmin < 5:
    primary = "Yates 校正 χ²"
else:
    primary = "未校正 Pearson χ²"
print(n, expected, "Tmin =", tmin, "→", primary)

# —— 效应量：样本 OR（交叉乘积）与 RD，Wald 95%CI ——
a, b = tab.iloc[0]          # A药：发生 a，未发生 b
c, d = tab.iloc[1]          # B药：发生 c，未发生 d
import numpy as np
or_sample = a*d / (b*c)
se_logor = np.sqrt(1/a + 1/b + 1/c + 1/d)
or_ci = np.exp(np.log(or_sample) + 1.96*np.array([-1, 1])*se_logor)
pA, pB = a/(a+b), c/(c+d)
rd = pA - pB
rd_ci = rd + 1.96*np.array([-1, 1])*np.sqrt(
    pA*(1-pA)/(a+b) + pB*(1-pB)/(c+d))
print(f"OR={or_sample:.3f} CI={or_ci.round(3)}")
print(f"RD={rd:.4f} CI={rd_ci.round(4)}")

# —— 保存本次输出 ——
tab.to_csv("output/adverse_events_table.csv", encoding="utf-8-sig")
pd.DataFrame([{"n": n, "tmin": tmin, "primary": primary,
               "pearson_chi2": chi2, "pearson_p": p_pearson,
               "yates_chi2": chi2_y, "yates_p": p_yates,
               "fisher_p": p_fisher,
               "or_sample": or_sample, "or_ci_low": or_ci[0], "or_ci_high": or_ci[1],
               "rd": rd, "rd_ci_low": rd_ci[0], "rd_ci_high": rd_ci[1]}]
             ).to_csv("output/adverse_events_result.csv", index=False)
```

说明：`stats.fisher_exact(tab)` 返回的 odds 是按传入列序定义的交叉乘积 OR；本例列序固定为[发生,未发生]，故为 3.5。`fisher_exact` 不给区间，需要区间时用上面的样本 OR + log-Wald；它与 R `fisher.test` 的条件 MLE/条件精确区间不是同一算法，报告时分别命名。Wald 区间只适用于非稀疏表；零格或边界比例时不要套，写"未估计该区间"并说明原因，禁止加 0.5 硬凑。

### 本次参考结果

| 药品 | 发生 | 未发生 | 合计 | 发生率 |
|---|---|---|---|---|
| A药 | 24 | 96 | 120 | 20.0% |
| B药 | 8 | 112 | 120 | 6.7% |

- n=240；期望频数 [[16,104],[16,104]]，Tmin=16；课程主要方法为未校正 Pearson。
- Pearson χ²=9.230769，df=1，P=0.00238。
- 具名对照：Yates χ²=8.112981，P=0.00439；Fisher 双侧 P=0.00383。不能因某个 P 较小就改选主要方法。
- A 相对 B 发生事件的**样本 OR=3.500**；log-Wald 95%CI（1.503，8.151），z=1.96。
- **RD=0.1333，即 13.3 个百分点**；Wald 95%CI（0.049，0.218）。

### R 版（同题）

```r
dat <- read.csv("datasets/teaching/adverse_events.csv")
tab <- table(drug = factor(dat$drug, levels = c("A药", "B药")),
             event = factor(dat$adverse_event, levels = c(1, 0)))
print(tab)
chisq.test(tab, correct = FALSE)        # Pearson
chisq.test(tab, correct = TRUE)         # Yates 对照
fisher.test(tab)                        # 条件 OR + 条件精确 CI，与样本 OR 分开命名

# 样本 OR（交叉乘积）与 RD
a <- tab[1,1]; b <- tab[1,2]; c <- tab[2,1]; d <- tab[2,2]
or <- a*d/(b*c)
exp(log(or) + c(-1,1)*1.96*sqrt(1/a+1/b+1/c+1/d))
pA <- a/(a+b); pB <- c/(c+d); pA-pB
```

### SPSS 读表与保存（本次未实跑）

原始 0/1 事件在交叉表里默认按升序把"未发生"放第一列。保留原变量，另建显示码 1=发生、2=未发生，并核对实际行列标签；交叉表应显示 A 行 24/96、B 行 8/112。个体数据先核对未加权；汇总频数输入先"数据 → 加权个案"。输出同时查看计数、期望与行百分比，按课程规则读"皮尔逊卡方"行，并核对风险估计的事件和组别方向。保存菜单"粘贴"出的 .sps、.spv 及 PDF。SPSS 若不给 RD CI，标明未计算，不能把本文件端点填成 SPSS 输出。

### 报告示范

> 教学模拟数据中，A 药不良事件发生率为 20.0%（24/120），B 药为 6.7%（8/120）。最小期望频数为 16，按预设课程规则采用未校正 Pearson χ² 检验，χ²(1)=9.231，P=0.002。A 相对 B 发生事件的样本 OR 为 3.50（log-Wald 95%CI：1.50～8.15）；RD 为 13.3 个百分点（Wald 95%CI：4.9～21.8）。数据只呈现发生率关联，不能由此证明药物造成事件。报告数字取自本次 `output/adverse_events_result.csv`。

OR 是 odds 之比，不能直接说"风险为 3.5 倍"；列名叫"不良事件"也不能替代真实的因果关系判定（不良反应需另有因果评价）。

---

## 例题 2：配对四格表 McNemar——两种快速检测试剂

### 场景与数据

课堂构造：同一批 120 份血样均用 A、B 两种试剂检测阳性/阴性。行代表 A 检测，列代表 B 检测。

| | B阳性 | B阴性 | 合计 |
|---|---|---|---|
| A阳性 | a=42 | b=18 | 60 |
| A阴性 | c=6 | d=54 | 60 |
| 合计 | 48 | 72 | 120 |

这是配对结果汇总，不能当独立两组。A、B 边缘阳性率为 50.0% 和 40.0%，差 10.0 个百分点。H₀ 是两种不一致类型的总体概率相同；b+c=24<40，按课程路线用双侧精确二项检验。一致对子 a、d 仍用于描述和分母。

### Python：精确二项法（含 b+c=0 保护）

```python
import numpy as np
from scipy import stats
from statsmodels.stats.contingency_tables import mcnemar

paired = np.array([[42, 18], [6, 54]])
a, b, c, d = paired.ravel()
m = b + c
if m == 0:
    print("无不一致对子：只作描述，不运行检验，也不能宣称等效")
else:
    p_exact = stats.binomtest(b, m, p=0.5, alternative="two-sided").pvalue
    print(f"b={b}, c={c}, 精确双侧 P={p_exact:.4f}")
    print(mcnemar(paired, exact=True))   # 与上面等价的 statsmodels 写法
```

### R 等价路线

```r
paired <- matrix(c(42, 18, 6, 54), nrow = 2, byrow = TRUE)
b <- paired[1,2]; c <- paired[2,1]
binom.test(b, b+c, p = 0.5, alternative = "two.sided")  # 精确
mcnemar.test(paired)   # 默认是校正渐近 χ²，只能作具名对照
```

`mcnemar.test()` 默认给校正渐近法，不是精确 P；SPSS 勾选 McNemar 后也要核对实际"精确/渐近""双侧"列名与脚注。

### 参考结果与报告

- 双侧精确二项：P=0.0227（可由 2·P[Binomial(24,0.5)≤6] 核算），报告 P=0.023；
- 具名对照：未校正渐近 χ²=6.000，df=1，P=0.0143；连续性校正 χ²=5.042，P=0.0247。三者不能混名。

> 120 份样品配对检测结果中，A 阳 B 阴 18 份、A 阴 B 阳 6 份；A、B 阳性检出率分别为 50.0% 和 40.0%，边缘差 10.0 个百分点。按预设课程规则采用 McNemar 双侧精确二项检验，P=0.023，数据支持两种试剂阳性检出率存在差异。配对率差的区间本例未计算，不套用独立率差区间。

把配对表 [[42,18],[6,54]] 直接当独立表做普通 Pearson，χ²≈45、P≈2×10⁻¹¹，那检验的是两检测结果的**关联**，问题完全不同；把边缘率拼成独立两组也违反配对设计。McNemar 比较边缘率，不评价一致性好坏。

---

## 课堂变式（均为课堂构造频数，用于条件与输入验收）

| 变式 | 完整输入与条件 | 主要教学点 |
|---|---|---|
| 临界 2×2 | 各 20 例，事件 2 vs 5；[[2,18],[5,15]]；Tmin=3.5 | 课程链选 Yates，χ²=0.693、P=0.405；不按 P 挑方法 |
| 小样本 Fisher | 各 11 例，事件 0 vs 4；[[0,11],[4,7]]；n=22、Tmin=2 | 因 n<40 选 Fisher 双侧，P=0.090；观察 0 不代表 T<1 |
| 观察零格 | [[0,20],[4,16]]，n=40，边际均正，Tmin=2 | 课程链选 Yates，χ²=2.500、P=0.114；Fisher 对照 P=0.106；样本 OR=0，log-Wald 区间不估 |
| 空边际 | [[30,0],[30,0]] | 退化表，只描述；不跑 Pearson/Yates，不把某软件 Fisher P=1 解释为"相同" |
| 零组分母 | [[0,0],[2,8]] | 第一组发生率写"不适用"，不能写 0% |
| 无不一致对子 | 配对表 [[42,0],[0,54]] | 不除以 b+c=0；单独描述，不证明等效 |
| 有序结局 | 治愈/显效/好转/无效 | 先问比较完整构成还是整体等级高低，显式定义顺序 |
| 缺少分母 | 只有"事件病例中各药占比" | 暂停率比较；不能编造用药人数 |

参考答案不能代替学生实际运行、保存和解释。
