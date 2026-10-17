# t 检验例题（references/examples）

全部例题使用本仓库 `datasets/teaching/` 中的模拟数据，统计数字由 `generate_datasets.py` 实跑生成（见该目录 `reference_outputs.txt`）。学生应自己重跑核对，不允许照抄本文件数字当结果。

---

## 例题 1：独立样本 t —— 两种制片工艺含量测定

数据：`datasets/teaching/tablet_assay.csv`（A 对照工艺、B 新工艺各 20 片，含量相当于标示量 %）。

### 路由

计量资料（assay_pct，%）；两组片剂互不重叠 → 独立两组；比较均数 → 独立样本 t 检验候选；先查正态性与方差齐性。

### Python 全过程

```python
import pandas as pd
from scipy import stats

df = pd.read_csv("datasets/teaching/tablet_assay.csv")
a = df.loc[df.process == "A_对照工艺", "assay_pct"]
b = df.loc[df.process == "B_新工艺", "assay_pct"]

print(a.describe(), b.describe())
print("Shapiro A:", stats.shapiro(a))   # W=0.955, P=0.449
print("Shapiro B:", stats.shapiro(b))   # W=0.942, P=0.264
print("Levene:", stats.levene(a, b, center="mean"))  # F=0.739, P=0.395
print("pooled t:", stats.ttest_ind(b, a, equal_var=True))   # t=2.338, P=0.0248
print("Welch t:", stats.ttest_ind(b, a, equal_var=False))   # t=2.338, P=0.0249
```

### 结果（参考答案）

| 组别 | n | x̄（%） | s（%） |
|---|---|---|---|
| A 对照工艺 | 20 | 98.497 | 0.958 |
| B 新工艺 | 20 | 99.257 | 1.093 |

- Shapiro–Wilk：A 组 W=0.955、P=0.449，B 组 W=0.942、P=0.264，均近似正态；
- Levene：F=0.739、P=0.395，方差齐，读合并方差 t 行；
- **t(38)=2.338，P=0.025**；均数差 B−A=0.760 个百分点，95%CI（0.102，1.418），Cohen's d=0.739。

### 报告示范

> 对照工艺组含量为 98.50%±0.96%（n=20），新工艺组为 99.26%±1.09%（n=20）。经 Shapiro–Wilk 检验两组均近似正态（P 均>0.05），Levene 检验方差齐（F=0.739，P=0.395），采用两独立样本 t 检验，t=2.338，df=38，P=0.025；新工艺组平均含量高 0.76 个百分点（95%CI：0.10～1.42）。两组含量均在药典限度（标示量 95.0%–105.0%）内，约 0.8 个百分点的差异虽达到 α=0.05 的统计学显著水平，但不具有制剂学专业意义。

教学点：**P<0.05 只说明"观测到的差异不太像抽样误差"，不说明差异重要。**

### SPSS 读图提示

独立样本检验输出有两列 t："假设等方差"（合并方差）与"不假设等方差"（Welch）。本例 Levene P=0.395，读第一行。

---

## 例题 2：配对 t（对数尺度）—— 生物等效性交叉试验

数据：`datasets/teaching/bioeq_cmax.csv`（24 名受试者，cmax_T、cmax_R 单位 ng/mL）。

### 为什么先取对数

Cmax 右偏、个体间差异远大于制剂间差异。BE 评价惯例对 Cmax、AUC 取自然对数：差值 ln(T)−ln(R) 近似正态，且 80%–125% 的等效界值在对数尺度上关于 0 对称。

### Python

```python
import numpy as np, pandas as pd
from scipy import stats

df = pd.read_csv("datasets/teaching/bioeq_cmax.csv")
ln_t, ln_r = np.log(df.cmax_T), np.log(df.cmax_R)
d = ln_t - ln_r                       # 配对差值
print(stats.shapiro(d))               # 先检查差值正态性：W=0.971, P=0.682
print(stats.ttest_rel(ln_t, ln_r))    # t=-0.624, df=23, P=0.539

# 几何均值比 GMR 及其 90% CI（等效性用 90% CI，不是 95%）
n = len(df)
m, se = d.mean(), d.std(ddof=1) / np.sqrt(n)
tcrit = stats.t.ppf(0.95, n - 1)
gmr = np.exp(m) * 100
ci = (np.exp(m - tcrit * se) * 100, np.exp(m + tcrit * se) * 100)
print(f"GMR={gmr:.2f}%  90%CI=({ci[0]:.2f}%, {ci[1]:.2f}%)")
```

### 结果（参考答案）

- 差值 Shapiro–Wilk 无异常（脚本数据按对数正态构造）；
- 配对 t：**t(23)=−0.624，P=0.539**；
- GMR = 98.10%，**90% CI（93.06%，103.41%）**，完全落在 80.00%–125.00% 界值内 → 生物等效成立。

### 关键反直觉点（必讲）

P=0.539 是"不能拒绝 T=R"，**这不是证明等效的逻辑**。若样本很小、置信区间很宽（比如 70%–140%），同样会 P>0.05，但明显不等效。BE 的判定只看 90% CI 是否落在界值内。完整规则与 AUC 平行分析见 `pharm-applications/bioequivalence` skill。

### 报告示范（Cmax 部分）

> 24 名受试者 Cmax 经自然对数转换后进行配对分析，受试制剂与参比制剂几何均值比为 98.10%，其 90% 置信区间为 93.06%～103.41%，位于 80.00%～125.00% 等效界值内，认为两制剂 Cmax 生物等效。

---

## 例题 3：单样本 t —— 片重与标示值（模板）

单样本没有配套数据，给最小模板：

```python
from scipy import stats
# 20 片片重(mg)，标示平均片重 100 mg
t, p = stats.ttest_1samp(weights, popmean=100)
```

报告："片重 x̄±s=＿±＿mg（n=20），与标示值 100 mg 比较，t(19)=＿，P=＿，95%CI（＿，＿）。"
注意药典片剂重量差异检查有专属的计数式判定规则（超限片数），不是 t 检验，不要混用。
