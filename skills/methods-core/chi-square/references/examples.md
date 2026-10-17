# χ² 检验例题（references/examples）

例 1 使用 `datasets/teaching/adverse_events.csv` 的实跑数据（见该目录 `reference_outputs.txt`）；例 2 为课堂假设数据，统计数字已用 Python 核算。学生须自行重跑核对。

---

## 例题 1：四格表 χ² —— 两药不良反应发生率

数据：A 药、B 药各 120 例，结局 adverse_event（1 发生 / 0 未发生）。

### 路由

计数资料（二分类）；两独立组（用药个体不重叠）；比较两个率 → 四格表 χ² 候选；先汇总表、算理论频数。

### Python 全过程

```python
import pandas as pd
from scipy import stats

df = pd.read_csv("datasets/teaching/adverse_events.csv")
tab = pd.crosstab(df.drug, df.adverse_event)
# adverse_event   0   1
# drug
# A药           96  24
# B药          112   8

chi2, p, dof, exp = stats.chi2_contingency(tab, correction=False)
chi2c, pc, _, _ = stats.chi2_contingency(tab, correction=True)
odds, pf = stats.fisher_exact(tab)
print(exp)     # [[16. 104.] [16. 104.]]
print(chi2, p, dof, odds, pf)
```

### 适用条件链

- 总 n=240 ≥ 40；
- 四个理论频数 16、104、16、104，全部 ≥5；
- → Pearson χ²（不校正）。同时输出校正值与 Fisher 仅作对照。

### 结果（参考答案）

| 药品 | 发生 | 未发生 | 合计 | 发生率 |
|---|---|---|---|---|
| A 药 | 24 | 96 | 120 | 20.0% |
| B 药 | 8 | 112 | 120 | 6.7% |

- Pearson χ²=9.231，df=1，**P=0.002**；
- 连续性校正 χ²=8.113，P=0.004；Fisher 精确 P=0.004（对照）；
- OR=3.500，95%CI（1.503，8.151）；率差 RD=13.3 个百分点，Wald 95%CI（4.9，21.8）。

### 报告示范

> A 药不良反应发生率为 20.0%（24/120），B 药为 6.7%（8/120）。总例数 n=240，最小理论频数为 16（≥5），采用四格表 Pearson χ² 检验，χ²=9.23，df=1，P=0.002；A 药发生不良反应的比值比 OR=3.50（95%CI：1.50～8.15）。在本观察数据中，A 药与较高的不良反应发生风险**存在关联**（不能表述为"A 药导致不良反应"，未控制混杂因素）。

### SPSS 读图提示

交叉表输出"卡方检验"表：
- "皮尔逊卡方"行 = Pearson；
- "连续性修正"行 = Yates 校正；
- "Fisher 精确检验"行；
- 表下脚注写明最小期望计数和小于 5 的格子数——先读脚注再读行。

---

## 例题 2：配对四格表 McNemar —— 两种快速检测试剂

### 场景

对同一批 120 份血样分别用 A、B 两种试剂检测某指标（阳性/阴性）。这是配对设计：每份样品产生一对结果，不能做独立样本 χ²。

| | B 阳性 | B 阴性 | 合计 |
|---|---|---|---|
| **A 阳性** | a=42（一致） | b=18 | 60 |
| **A 阴性** | c=6 | d=54（一致） | 60 |
| 合计 | 48 | 72 | 120 |

关键：一致对子 a、d 对两种方法的比较没有信息，只看不一致对子 **b=18、c=6**。

### 条件与计算

- b+c=24 < 40 → 本科教材口径用连续性校正公式或二项精确法；
- 未校正：χ²=(b−c)²/(b+c)=6.000，P=0.014；
- 校正：χ²=(|b−c|−1)²/(b+c)=5.042，P=0.025；
- 双侧精确（Binomial(24, 0.5)，P(X≤6)×2）：P=0.023。

### Python

```python
from statsmodels.stats.contingency_tables import mcnemar
# 配对四格表按 [[a,b],[c,d]] 排列
paired = [[42, 18], [6, 54]]
print(mcnemar(paired, exact=True).pvalue)                  # 精确：0.0227
print(mcnemar(paired, exact=False, correction=True).pvalue)  # 连续性校正：0.0247
```

（scipy 不含 McNemar，须用 statsmodels；R 用 `mcnemar.test`，SPSS 在交叉表中勾选 McNemar。）

### 报告示范

> 120 份样品配对检测结果显示，两种试剂均阳性 42 份、均阴性 54 份，结果不一致 24 份（A 阳 B 阴 18 份，A 阴 B 阳 6 份）。不一致对子数 b+c=24（<40），采用 McNemar 精确检验，P=0.023，可认为两种试剂的阳性检出率差异有统计学意义，A 试剂阳性检出率较高。

### 教学点

- 若错用独立 χ²：a、d 两个大格子会"稀释"差异，可能得出错误结论；配对信息只在 b、c 里；
- McNemar 只回答"边缘率是否相同"，不回答"两种方法一致性好不好"——一致性评价用 Kappa（超纲时点名即可）。

---

## 课堂变式建议（教师用）

| 变式 | 数据改动 | 想暴露的错误 |
|---|---|---|
| 临界卡方 | 两组各 20 例，事件 3 vs 8 | 出现 1≤T<5，必须读校正/Fisher 行 |
| Fisher 场景 | 两组共 22 例，事件 0 vs 4 | n<40 且有 T<1，普通 χ² 失效 |
| 等级误判 | 结局改为治愈/显效/好转/无效 | χ² 丢序，应转秩和检验 |
| 构成比误读 | 给"事件病例中各药占比"无分母 | 构成比不是率，不能直接比较 |
