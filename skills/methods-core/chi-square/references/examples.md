# χ² 检验例题（references/examples）

例1使用`datasets/teaching/adverse_events.csv`的教学模拟数据；例2是课堂构造的配对频数。参考数值由Python实际复算。本文件的Python调用从仓库根目录运行，计算与保存由`scripts/analyze_teaching.py`完成，不运行数据生成脚本覆盖输入。R代码另在WebR/R 4.6.0执行过；桌面R与SPSS仍须在所用环境核对后再标为通过。

---

## 例题1：两独立组不良事件发生率

A药、B药各120例；adverse_event为1=发生、0=未发生。按本教学题假设病例间独立；真实数据还须核对中心、批次和重复记录等设计信息，不能仅从ID判断独立。

### 路由与主要规则

研究问题是两个独立组的二分类发生率是否不同。先核对分子分母和编码，再固定行[A药,B药]、列[发生1,未发生0]。本次课程链：n<40或Tmin<1用Fisher双侧，否则Tmin<5用Yates，其余用未校正Pearson。此链的指定教材原文仍待核，不能写成全部教材的普遍定理。

### Python全过程：检查方向、执行与保存

```python
import json
import subprocess
import sys
from pathlib import Path
import pandas as pd

df = pd.read_csv("datasets/teaching/adverse_events.csv")
required = ["drug", "adverse_event"]
if not set(required).issubset(df.columns):
    raise ValueError("缺少分组或结局列")
if df[required].isna().any().any():
    raise ValueError("先记录并处理缺失；不得静默删除")
if not df["drug"].isin(["A药", "B药"]).all():
    raise ValueError("未知分组；不能通过重排丢弃")
if not df["adverse_event"].isin([0, 1]).all():
    raise ValueError("事件只接受0/1；先核对编码")
tab = pd.crosstab(df["drug"], df["adverse_event"]).reindex(
    index=["A药", "B药"], columns=[1, 0], fill_value=0
)
print(tab)  # [[24,96],[8,112]]，事件优先

out = Path("output/teaching")
subprocess.run([
    sys.executable, "scripts/analyze_teaching.py",
    "--output-dir", str(out), "--t-policy", "course"
], check=True)
r = json.loads((out / "results.json").read_text(encoding="utf-8"))["adverse_events"]
assert r["table"] == tab.to_numpy().tolist()
print(json.dumps(r, ensure_ascii=False, indent=2))
```

共用脚本检验退化表、计算具名方法与效应区间，并写出`adverse_events_table.csv`、`results.json`、`summary.csv`和`summary.txt`。教学表与统计输出均保留，不从参考答案补数字。

### 本次参考结果

| 药品 | 发生 | 未发生 | 合计 | 发生率 |
|---|---|---|---|---|
| A药 | 24 | 96 | 120 | 20.0% |
| B药 | 8 | 112 | 120 | 6.7% |

- n=240；期望频数为[[16,104],[16,104]]，Tmin=16；课程主要方法为未校正Pearson。
- Pearson χ²=9.230769，df=1，P=0.0023798165。
- 具名对照：Yates χ²=8.112981，P=0.0043949400；Fisher双侧P=0.0038347022。不能因某个P较小就改选主要方法。
- A相对B发生事件的**样本OR=3.500**；log-Wald95%CI=[1.502954,8.150614]，使用z=1.96。
- **RD=0.133333，即13.3个百分点**；独立比例Wald95%CI=[0.048988,0.217678]，换算为[4.9,21.8]个百分点。本例近似区间不应无条件推广至稀疏表。

数字来源对应`results.json`中的：

| 报告项目 | 字段路径（根键adverse_events下） |
|---|---|
| 实际表与期望频数 | table、expected；标签另见row_labels、column_labels |
| 主方法 | primary_method |
| 主要检验 | tests.pearson.statistic / df / pvalue |
| 方法对照 | tests.yates、tests.fisher（Fisher不填χ²/df） |
| 样本OR及算法 | effects.odds_ratio_sample.estimate / ci95 / ci_method |
| RD及算法 | effects.risk_difference.estimate / ci95 / ci_method |

### R效应输出补充（接主文件轨B运行；WebR已执行）

```r
# 使用主文件已校验方向的tab；样本OR/Wald区间与Fisher条件OR分开。
a <- as.numeric(tab[1, 1]); b <- as.numeric(tab[1, 2])
c <- as.numeric(tab[2, 1]); d <- as.numeric(tab[2, 2])
stopifnot(all(is.finite(tab)), all(tab >= 0), all(tab == floor(tab)),
          all(rowSums(tab) > 0), all(colSums(tab) > 0))
expected <- outer(rowSums(tab), colSums(tab)) / sum(tab)
sample_or <- if (b * c > 0) a * d / (b * c) else Inf
pA <- a / (a + b); pB <- c / (c + d)
rd <- pA - pB
or_ci <- rd_ci <- c(NA_real_, NA_real_)
ci_status <- "not_estimated_sparse_or_zero_cell"
if (all(tab > 0) && min(expected) >= 5) {
  or_ci <- exp(log(sample_or) + c(-1, 1) * 1.96 * sqrt(sum(1 / tab)))
  rd_ci <- rd + c(-1, 1) * 1.96 * sqrt(
    pA * (1 - pA) / (a + b) + pB * (1 - pB) / (c + d))
  ci_status <- "Wald_z_1.96"
} else {
  message("稀疏或零格：保留可定义点估计，当前片段未估计适当区间；不得加0.5凑值")
}
effects <- list(direction = "A药相对B药，事件=发生",
                sample_OR = sample_or, log_Wald_OR_CI95 = or_ci,
                RD = rd, independent_Wald_RD_CI95 = rd_ci, ci_status = ci_status)
capture.output(effects, file = "output/chi_square_R/effects.txt")
# 如查看fisher.test(tab)的estimate/conf.int，应标条件MLE/条件精确CI；
# 不把它们当作sample_OR/log-Wald区间。上面的Wald计算只演示本非稀疏表。
```

### SPSS读表与保存（本次未实跑）

保留原始0/1事件，另建显示码1=发生、2=未发生；交叉表实际应为A行24/96、B行8/112。个体数据核对未加权；汇总频数输入先按人数加权。输出同时查看计数、期望与行百分比，按课程规则读“皮尔逊卡方”行，并核对风险估计的事件和组别方向。保存菜单粘贴语法.sps、输出.spv及PDF。若本机过程没有给RD CI，标明未计算；不能把本文件端点填成SPSS输出。

### 报告示范

> 教学模拟数据中，A药不良事件发生率为20.0%（24/120），B药为6.7%（8/120）。最小期望频数为16，按预设课程规则采用未校正Pearsonχ²检验，χ²(1)=9.231，P=0.002。A相对B发生事件的样本OR为3.50（log-Wald95%CI：1.50～8.15）；RD为13.3个百分点（Wald95%CI：4.9～21.8）。数据呈现发生率关联，不能由此证明药物造成事件。报告数字取自本次output/teaching/results.json的adverse_events字段。

OR表示odds之比，不能直接说“风险为3.5倍”。不良事件与已确认因果关系的不良反应也不能仅凭列名互换。

---

## 例题2：配对四格表McNemar——两种快速检测试剂

### 场景与数据

课堂构造：同一批120份血样均用A、B两种试剂检测阳性/阴性。行代表A检测，列代表B检测。

| | B阳性 | B阴性 | 合计 |
|---|---|---|---|
| A阳性 | a=42 | b=18 | 60 |
| A阴性 | c=6 | d=54 | 60 |
| 合计 | 48 | 72 | 120 |

本表是配对结果汇总，不能作为独立两组。A、B边缘阳性率为50.0%和40.0%，差10.0个百分点。H₀为两种不一致类型的总体概率相同；b+c=24，按本课程路线用双侧精确二项检验。一致对子仍用于描述与分母。

### Python执行、零值保护与保存

运行例1的共用脚本后，`results.json`的`mcnemar_demo`保存本表、边缘率和具名检验。下面直接按精确定义独立核对，并另存真实结果：

```python
import json
from pathlib import Path
import numpy as np
import scipy
from scipy import stats

paired = np.asarray([[42, 18], [6, 54]], dtype=float)
if (paired.shape != (2, 2) or not np.isfinite(paired).all()
        or (paired < 0).any() or not np.equal(paired, np.floor(paired)).all()):
    raise ValueError("配对频数必须是2×2非负整数")
a, b, c, d = paired.astype(int).ravel()
m = int(b + c)
result = {"table": paired.astype(int).tolist(), "b": int(b), "c": int(c),
          "discordant_pairs": m, "software": f"SciPy {scipy.__version__}"}
if m == 0:
    result.update(status="descriptive_only", method=None, pvalue=None,
                  note="无不一致对子；本流程不运行检验，不能证明相同或等效")
else:
    result.update(status="computed", method="McNemar exact binomial two-sided",
                  pvalue=float(stats.binomtest(int(b), m, p=0.5,
                                             alternative="two-sided").pvalue))
out = Path("output/teaching")
out.mkdir(parents=True, exist_ok=True)
(out / "mcnemar_exact_check.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(result)
```

如改用statsmodels，须先处理m=0，再调用`mcnemar(paired, exact=True)`；不要把渐近统计量填入精确结果。

### R等价精确路线（WebR已执行）

```r
paired <- matrix(c(42, 18, 6, 54), nrow = 2, byrow = TRUE,
                 dimnames = list(A = c("阳性", "阴性"), B = c("阳性", "阴性")))
stopifnot(all(is.finite(paired)), all(paired >= 0), all(paired == floor(paired)))
b <- paired[1, 2]; c <- paired[2, 1]; m <- b + c
out <- "output/chi_square_R"
dir.create(out, recursive = TRUE, showWarnings = FALSE)
if (m == 0) {
  capture.output("无不一致对子：本流程不运行检验", file = file.path(out, "mcnemar.txt"))
} else {
  exact <- binom.test(b, m, p = 0.5, alternative = "two.sided")
  capture.output(paired, exact, sessionInfo(), file = file.path(out, "mcnemar.txt"))
}
```

`mcnemar.test(paired)`默认是校正渐近χ²，不是上述精确P。SPSS交叉表勾选McNemar后，须核对实际双侧精确/渐近列和脚注；本次未核全版本自动行为，不保证菜单勾选即自动满足课程算法。

### 参考结果与报告

- 双侧精确二项：P=0.0226558447，报告P=0.023；本例可由2P[Binomial(24,0.5)≤6]核算。
- 具名对照：未校正渐近χ²=6.000，df=1，P=0.0143058784；连续性校正χ²=5.041667，df=1，P=0.0247446720。三者不能混名。

> 120份样品配对检测结果中，A阳B阴18份、A阴B阳6份；A、B阳性检出率分别为50.0%和40.0%，边缘差10.0个百分点。按预设课程规则采用McNemar双侧精确二项检验，P=0.023，数据支持两种试剂阳性检出率存在差异。边缘率差的配对CI本流程尚未计算，不套用独立率差区间。来源为本次mcnemar_exact_check.json及results.json的mcnemar_demo。

直接对配对表[[42,18],[6,54]]做普通Pearson，实际χ²=45、P约1.97×10⁻¹¹，检验的是两检测结果的关联；将边缘率另拼为独立两组也违反设计。误用不保证“稀释”差异。McNemar比较边缘率，不判断一致性好不好。

---

## 课堂变式（均为课堂构造频数）

| 变式 | 完整输入与条件 | 主要教学点 |
|---|---|---|
| 临界2×2 | 各20例，事件2vs5；[[2,18],[5,15]]；Tmin=3.5 | 本次课程用Yates，χ²=0.692641、P=0.4052676330；不按P挑方法 |
| 小样本Fisher | 各11例，事件0vs4；[[0,11],[4,7]]；n=22、Tmin=2 | 因n<40选Fisher双侧，P=0.0902255639；观察0不能推出T<1 |
| 观察零格 | [[0,20],[4,16]]，n=40，边际均正，Tmin=2 | 本次课程用Yates，χ²=2.500000、P=0.1138462980；Fisher双侧为对照，P=0.1060291060。样本OR=0，log-Wald区间未估计 |
| 空边际 | [[30,0],[30,0]] | 本流程仅描述；不跑Pearson/Yates，不把某软件Fisher P=1解释为相同 |
| 零组分母 | [[0,0],[2,8]] | 第一组发生率“不适用”，不能写0% |
| 无不一致对子 | 配对表[[42,0],[0,54]] | 不除以b+c=0；单独描述，不证明等效 |
| 有序结局 | 治愈/显效/好转/无效 | 先问完整构成还是整体等级高低，显式定义顺序 |
| 缺少分母 | 只有“事件病例中各药占比” | 暂停率比较；不能编造用药人数 |

这些变式用于条件和输入验收；软件实跑范围以仓库验证记录为准。参考答案不能代替学生实际运行、保存和解释。
