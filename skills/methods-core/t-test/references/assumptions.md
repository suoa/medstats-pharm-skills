# t 检验前提条件详解（references/assumptions）

SKILL.md 的展开材料。学生问"为什么要做正态性检验""P=0.049 算不算正态"时读这里。

## 一、独立性（三类 t 检验共同的前提）

- 结合抽样/实验单位与测量结构核查独立性，不能只凭ID不同、两组个体不重叠来证明。随机分组还影响因果解释；观察性比较即使可作均数检验，也不能因此宣布用药导致差异。
- 配对 t 要求"对子之间独立"，不要求两组独立——同一对子内的两个值本来就相关。
- 常见违反：同一动物多次测量当作多只动物；每工艺仅一批却把该批多片当作多个独立工艺重复；整群抽样忽略群内相关。两个相关时点可按配对设计核查；同一对象≥3时点、批次或整群结构先回路由讨论，不直接套普通独立t。
- 配对先核对象键与每条件记录唯一性，按键匹配后选完整对，并记录纳入/缺失对数；不得各自去缺失后按行号拼接。将一侧记录重排，按键对齐后的差值、n和t/P必须不变；重复键不能造成多对多匹配。

## 二、正态性

### 检验对象（最容易错）

| 方法 | 检验正态性的对象 |
|---|---|
| 单样本 t | 原始观测值 |
| 配对 t | **差值 d**（不是两组原始值各自正态） |
| 独立样本 t | 两组各自的观测值 |

### 可用工具

- Shapiro–Wilk：至少需要3个有效观测。R的`shapiro.test`允许3–5000；SciPy提示N>5000时P可能不准确。课堂可优先在小样本练习，但50不是软件上限；小样本也可能因效能不足未检出非正态，大样本可能检出轻微偏离；
- 图形：直方图、Q-Q 图（教学中推荐与检验并列，培养目测能力）；
- 偏度/峰度仅作参考。

### 判定与处置

1. P>0.05写“未发现足以拒绝正态性的证据”，不写“证明/满足正态”。同时核Q-Q图、离群值、各组样本量及专业背景；图形本身也不保证小样本前提成立；
2. 轻度偏离时结合各组n、尾部、平衡性与异常值判断t的稳健性并记录理由；n≥30不是保证，总n大不能弥补某组极小。n=8也不自动禁止t或指定U；
3. 明显偏态时可讨论有专业意义的变换，如对正浓度取对数；变换后重新核查，并说明估计尺度已改变。零值/负值不能直接取对数，也不随意加常数；
4. 需要改用相应秩方法时先确认研究问题：Wilcoxon符号秩的位置解释需要相应对称条件；Mann–Whitney不自动检验均数或中位数相等。教师可给限定题目的默认路线，但不能宣称所有非正态数据都可无条件替代。方法有实质争议时保留描述并交教师核查，不批量试检验挑较小P。

### 教学提醒

- 正态性检验 P=0.052 与 P=0.048 在证据强度上几乎没有差别，不要把 0.05 当成悬崖；结合图形、样本量和专业背景判断，并把判断写进 DECISIONS.md。
- 离群值先查录入错误和实验事故，不能"为了显著"删数据；保留时做含/不含离群值的敏感性分析。

## 三、方差齐性（仅独立样本 t）

- 查看结果前只锁定一套主要分析规则，记录软件与方向；不要求学生自行维护多套配置。教师已规定的课程读表规则直接采用；未指定的通用分析可预设Welch，不能看完结果再切换。
- **课程路线**：本仓库例题固定经典Levene（中心mean）。未舍入P>0.05，写“未发现方差不齐的证据”，按课程约定读pooled；P≤0.05读Welch。该分流是教学规则，非“P>0.05证明方差相等”，也不声称所有教材/分析都必须先预检。
- **预设Welch路线**：不要求方差齐；Levene若作为诊断输出，不改变主要方法。均数差CI与自由度也用Welch，不能引用pooled CI。
- mean为经典Levene；median为常称Brown–Forsythe的稳健变体。`car::leveneTest`默认median，SciPy `stats.levene`也默认median；要与本例mean一致必须显式设置。SPSS算法与输出行须按实际过程/版本核对，不写“SPSS通用默认median”。
- SPSS常见独立样本输出列出“假设等方差/不假设等方差”两行；按预设课程或Welch规则读行。部分新版本需另选方差齐性输出，本仓库尚未在SPSS实机验收。基础R已有WebAssembly实跑；桌面R及car包未据此视为通过。
- `.050`是显示值，不必等于真实P=.05。提高显示精度至能判断分支；仍不清楚则交教师核查。若课程规定P≤.05用Welch，构造分支值.0496和.0504虽都显示.050，却分别选Welch和pooled；这些是分支测试值，不是本例实跑结果。

## 四、前提检查的最小代码块（Python）

以下是已有清理后`a`、`b`与按ID对齐`x_t`、`x_r`时的最小模板；完整可运行的读 CSV 例题见同目录 `examples.md`，图形与设计证据须另核查。不能运行时如实标"未执行"。

```python
from scipy import stats

# Independent samples; inputs must already be checked.
for name, g in [("A", a), ("B", b)]:
    w, p = stats.shapiro(g)
    print(name, "Shapiro W=%.3f P=%.3f" % (w, p))
F, pL = stats.levene(a, b, center="mean")
print("Levene F=%.3f P=%.3f" % (F, pL))

# Paired samples: align by ID, then keep complete pairs before subtraction.
d = x_t - x_r
w, p = stats.shapiro(d)
print("差值 Shapiro W=%.3f P=%.3f" % (w, p))
```

## 五、决策速查

```
计量资料，研究问题为1–2组均数/均数差，设计与实验单位已有依据
单样本：核观测值；配对：先匹配完整对，再核差值；独立两组：分别核组内分布
结合图形、Shapiro、各组n与异常值判断；有实质争议先交教师，不靠P通关
适合独立两组t：执行预先指定的课程Levene(mean)分流，或预设Welch
需变换/秩方法：重新确认目标量、尺度及方法前提，不把秩结果称为均数检验
正式交叉、等效/非劣效、重复测量或批次结构：返回相应设计流程
```

核查依据：[R Shapiro](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/shapiro.test.html)、[SciPy Shapiro](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.shapiro.html)、[R t.test](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/t.test.html)、[car Levene](https://cran.r-project.org/web/packages/car/refman/car.html)、[SciPy Levene](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.levene.html)、[R Wilcoxon](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/wilcox.test.html)。这些文档用于核软件算法；教师指定教材的版次及相关页码由原文核查，不编造教材依据。
