#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医学统计Skills 教学数据集生成脚本
固定随机种子，保证任何人重跑得到完全相同的 CSV。
数据全部为教学模拟数据，不含任何真实受试者信息。
运行：python3 generate_datasets.py
"""
import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path

HERE = Path(__file__).parent
SEED = 20261017
rng = np.random.default_rng(SEED)

# ---------------------------------------------------------------------------
# 数据集 1：bioeq_cmax.csv
# 24 名健康受试者，双周期双交叉设计，受试制剂 T 与参比制剂 R 的 Cmax（ng/mL）
# 教学用途：配对 t 检验（差值为 ln(T)-ln(R)）、生物等效性 90%CI 80–125%
# 构造参数：个体间变异大、个体内变异 CV≈15%、T/R 几何均值比≈1.02（等效）
# ---------------------------------------------------------------------------
n = 24
subject = np.arange(1, n + 1)
log_base = np.log(500.0)                 # 总体 ln(Cmax) 中心
subj_eff = rng.normal(0, 0.35, n)        # 个体间差异（大）
within = 0.15                            # 个体内 ln-SD（CV≈15%）
log_ratio_mean = np.log(1.02)            # 真实 T/R 比 1.02

log_r = log_base + subj_eff + rng.normal(0, within, n)
log_t = log_base + subj_eff + log_ratio_mean + rng.normal(0, within, n)

df1 = pd.DataFrame({
    "subject_id": [f"S{i:02d}" for i in subject],
    "cmax_R": np.round(np.exp(log_r), 1),
    "cmax_T": np.round(np.exp(log_t), 1),
})
df1.to_csv(HERE / "bioeq_cmax.csv", index=False, encoding="utf-8-sig")

# 参考分析（对数尺度配对 t 检验 + 90%CI 反算）
d = df1["cmax_T"].to_numpy() / df1["cmax_R"].to_numpy()
ln_d = np.log(df1["cmax_T"].to_numpy()) - np.log(df1["cmax_R"].to_numpy())
t1, p1 = stats.ttest_rel(np.log(df1["cmax_T"]), np.log(df1["cmax_R"]))
mean_ln = ln_d.mean()
se_ln = ln_d.std(ddof=1) / np.sqrt(n)
tcrit = stats.t.ppf(0.95, df=n - 1)
ci90_ratio = (np.exp(mean_ln - tcrit * se_ln) * 100,
              np.exp(mean_ln + tcrit * se_ln) * 100)
gmr = np.exp(mean_ln) * 100

# ---------------------------------------------------------------------------
# 数据集 2：tablet_assay.csv
# 两种制片工艺各 20 片的含量测定结果（相当于标示量的百分比，%）
# 教学用途：独立样本 t 检验、方差齐性、"统计显著但专业上无意义"的讨论
# 构造：A 旧工艺 98.5±1.2，B 新工艺 99.5±1.0（药典含量限度通常 95.0–105.0%）
# ---------------------------------------------------------------------------
n2 = 20
assay_A = rng.normal(98.5, 1.2, n2)
assay_B = rng.normal(99.5, 1.0, n2)
df2 = pd.DataFrame({
    "tablet_id": [f"A{i:02d}" for i in range(1, n2 + 1)] +
                 [f"B{i:02d}" for i in range(1, n2 + 1)],
    "process": ["A_对照工艺"] * n2 + ["B_新工艺"] * n2,
    "assay_pct": np.round(np.r_[assay_A, assay_B], 2),
})
df2.to_csv(HERE / "tablet_assay.csv", index=False, encoding="utf-8-sig")

# 参考答案必须从"落盘后的 CSV"回读计算——学生重跑的是这份取整后的数据，
# 直接用未取整的内存数组会让参考答案与学生结果对不上。
_saved2 = pd.read_csv(HERE / "tablet_assay.csv")
assay_A = _saved2.loc[_saved2.process == "A_对照工艺", "assay_pct"].to_numpy()
assay_B = _saved2.loc[_saved2.process == "B_新工艺", "assay_pct"].to_numpy()
# Shapiro 正态性（分组）
sw_A = stats.shapiro(assay_A)
sw_B = stats.shapiro(assay_B)
# Levene 方差齐性（center="mean" 即经典 Levene；SPSS 默认中位数=Brown–Forsythe）
lev = stats.levene(assay_A, assay_B, center="mean")
# 合并方差 t 检验（方差齐）
t2, p2 = stats.ttest_ind(assay_B, assay_A, equal_var=True)
t2w, p2w = stats.ttest_ind(assay_B, assay_A, equal_var=False)
mdiff = assay_B.mean() - assay_A.mean()
spooled = np.sqrt(((n2 - 1) * assay_A.var(ddof=1) + (n2 - 1) * assay_B.var(ddof=1))
                  / (2 * n2 - 2))
ci95_diff = (mdiff - stats.t.ppf(0.975, 2 * n2 - 2) * spooled * np.sqrt(2 / n2),
             mdiff + stats.t.ppf(0.975, 2 * n2 - 2) * spooled * np.sqrt(2 / n2))
cohen_d = mdiff / spooled

# ---------------------------------------------------------------------------
# 数据集 3：adverse_events.csv
# 两种药品不良反应发生情况的四格表原始记录（每药 120 例）
# A 药事件 24 例（20.0%），B 药事件 8 例（6.7%）
# 教学用途：四格表卡方（n≥40、理论频数≥5）；率差、OR
# ---------------------------------------------------------------------------
nA = nB = 120
kA, kB = 24, 8
a_flag = np.r_[np.ones(kA, dtype=int), np.zeros(nA - kA, dtype=int)]
b_flag = np.r_[np.ones(kB, dtype=int), np.zeros(nB - kB, dtype=int)]
rng.shuffle(a_flag)
rng.shuffle(b_flag)
df3 = pd.DataFrame({
    "subject_id": [f"PA{i:03d}" for i in range(1, nA + 1)] +
                  [f"PB{i:03d}" for i in range(1, nB + 1)],
    "drug": ["A药"] * nA + ["B药"] * nB,
    "adverse_event": np.r_[a_flag, b_flag],   # 1=发生 0=未发生
})
df3.to_csv(HERE / "adverse_events.csv", index=False, encoding="utf-8-sig")

table = np.array([[kA, nA - kA], [kB, nB - kB]])
chi2, p3, dof, expected = stats.chi2_contingency(table, correction=False)
chi2_y, p3_y, _, _ = stats.chi2_contingency(table, correction=True)
odds, p_fisher = stats.fisher_exact(table)
rate_A, rate_B = kA / nA * 100, kB / nB * 100
or_ci_lo = np.exp(np.log(odds) - 1.96 * np.sqrt(
    1 / kA + 1 / (nA - kA) + 1 / kB + 1 / (nB - kB)))
or_ci_hi = np.exp(np.log(odds) + 1.96 * np.sqrt(
    1 / kA + 1 / (nA - kA) + 1 / kB + 1 / (nB - kB)))

# ---------------------------------------------------------------------------
# 输出参考答案（写入 reference_outputs.txt，供 skill 例题核对）
# ---------------------------------------------------------------------------
out = []
out.append("医学统计Skills 教学数据集 · 参考答案（由 generate_datasets.py 实跑生成）")
out.append(f"随机种子：{SEED}\n")

out.append("【数据集1 bioeq_cmax.csv】配对 t（对数尺度）与生物等效性")
out.append(f"  T/R 几何均值比 GMR = {gmr:.2f}%")
out.append(f"  配对 t（ln T vs ln R）：t = {t1:.3f}, df = {n-1}, p = {p1:.4f}")
out.append(f"  GMR 的 90% CI = ({ci90_ratio[0]:.2f}%, {ci90_ratio[1]:.2f}%)")
out.append(f"  判定：90%CI 完全落在 80.00–125.00% 内 → 生物等效成立\n")

out.append("【数据集2 tablet_assay.csv】独立样本 t 检验")
out.append(f"  A 对照工艺：mean = {assay_A.mean():.3f}, SD = {assay_A.std(ddof=1):.3f}, "
           f"Shapiro W = {sw_A.statistic:.3f}, p = {sw_A.pvalue:.3f}")
out.append(f"  B 新工艺  ：mean = {assay_B.mean():.3f}, SD = {assay_B.std(ddof=1):.3f}, "
           f"Shapiro W = {sw_B.statistic:.3f}, p = {sw_B.pvalue:.3f}")
out.append(f"  Levene 方差齐性：F = {lev.statistic:.3f}, p = {lev.pvalue:.3f}")
out.append(f"  合并方差 t 检验：t = {t2:.3f}, df = {2*n2-2}, p = {p2:.4f}")
out.append(f"  Welch t（对照）：t = {t2w:.3f}, p = {p2w:.4f}")
out.append(f"  均数差 B−A = {mdiff:.3f} 个百分点，95%CI = ({ci95_diff[0]:.3f}, {ci95_diff[1]:.3f})")
out.append(f"  Cohen d = {cohen_d:.3f}")
out.append(f"  教学点：统计可能显著，但约 1 个百分点的差异远小于药典含量允许波动，无专业意义\n")

out.append("【数据集3 adverse_events.csv】四格表卡方")
out.append(f"  A 药不良反应率 = {rate_A:.1f}%（{kA}/{nA}），B 药 = {rate_B:.1f}%（{kB}/{nB}）")
out.append(f"  理论频数：{expected.flatten().round(2)}（均 ≥5），总 n = {nA+nB}（≥40）→ 普通卡方")
out.append(f"  Pearson χ² = {chi2:.3f}, df = {dof}, p = {p3:.4f}")
out.append(f"  连续性校正 χ² = {chi2_y:.3f}, p = {p3_y:.4f}（本科教材要求时报告）")
out.append(f"  OR = {odds:.3f}，95%CI = ({or_ci_lo:.3f}, {or_ci_hi:.3f})")
out.append(f"  Fisher 精确检验（对照）p = {p_fisher:.4f}")

(HERE / "reference_outputs.txt").write_text("\n".join(out), encoding="utf-8")
print("\n".join(out))
