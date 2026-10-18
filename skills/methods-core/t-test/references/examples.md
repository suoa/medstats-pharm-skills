# t 检验例题（references/examples）

例题1、2使用本仓库`datasets/teaching/`中的**示意构造数据**；单样本例题3仅为待填输入的模板。数据生成与学生分析分开：不要为得到答案重建原始数据；读取已提交CSV，运行共同分析脚本，保存本次真实结果后再写报告。本页参考数字来自对提交CSV的复算，不能冒充学生本次运行。

在仓库根目录先运行一次（Python依赖见仓库安装说明；输出目录必须尚不存在，空目录也拒绝）：

```bash
python scripts/analyze_teaching.py --output-dir output/teaching --t-policy course
```

该命令采用事先指定的课程Levene(mean)路线，保存`results.json`、`summary.csv`、`summary.txt`，以及事件表`adverse_events_table.csv`、图形`diagnostics.png`和逐点数据`diagnostic_points.csv`，共六份产物。若教师事先指定通用Welch路线，改用`--t-policy welch`并读取对应主结果；不能看P后更换。JSON保留输入、版本、方向与未舍入结果，文本与表格供阅读。执行失败保留错误，不能复制下方参考值生成伪输出；不能保存时如实写“已计算，尚未保存”。

下列读取块复用刚生成的同一轮结果，无须再次计算。需要重跑时另选输出目录，并将本页各读取块的路径一起改到该目录；上一轮文件保留。

本次有Python数值与文件输出的实跑验收；脚本数值不等于图形前提已经核验，Q-Q图仍须学生/教师实际查看。基础R已有WebR/R 4.6.0数值复算及模板执行，桌面R与SPSS尚待实机验证。三轨可选不等于三轨均已验证，实际范围见仓库验证记录。

---

## 例题 1：独立样本 t —— 两种制片工艺含量测定

数据：`datasets/teaching/tablet_assay.csv`（A 对照工艺、B 新工艺各 20 片，含量相当于标示量 %）。

### 路由

计量资料（assay_pct，标示量百分比）；目标为B−A均数差。**本计算练习预设各片观测独立**，并用课程Levene(mean)路线；CSV的ID不同不能证明真实工艺重复独立。真实研究须核每工艺批次数及抽样单位；每工艺仅一批而多片取样，不能据此推广工艺效果。先检查两组分布、异常值及设计依据，再按预设规则分析。

### Python：读取本次已保存结果

```python
import json
from pathlib import Path

results = json.loads(Path("output/teaching/results.json").read_text(encoding="utf-8"))
case = results["tablet_assay"]
primary = case["tests"][case["primary_method"]]
print("Direction:", case["direction"])
print("Groups:", case["groups"])
print("Levene:", case["levene"])
print("Primary method:", case["primary_method"])
print("Primary result:", primary)
print("Cohen d (pooled SD):", case["cohens_d"])
```

分析脚本实际计算两种t的统计量、df、P、均数差和各自95%CI，并输出以合并SD为分母的可选d；报告读取`tablet_assay.tests.<primary_method>`。本例课程分流选pooled，Welch只标对照。JSON中的`groups.A/B`保存n、均数、SD和Shapiro结果，`levene`记录中心算法；不从参考答案手填结果文件。

### 结果（参考答案）

| 组别 | n | x̄（%） | s（%） |
|---|---|---|---|
| A 对照工艺 | 20 | 98.497 | 0.958 |
| B 新工艺 | 20 | 99.257 | 1.093 |

- Shapiro–Wilk：A组W=0.955、P=0.449，B组W=0.942、P=0.264；未发现足以拒绝正态性的证据，仍须查看Q-Q图与异常值，不能仅据这两个P宣布正态；
- Levene(mean)：F=0.739、P=0.395；未发现方差不齐的证据，按本题指定课程规则读合并方差t；
- **t(38)=2.338，P=0.025**；均数差 B−A=0.760 个百分点，95%CI（0.102，1.418），Cohen's d=0.739。
- 预设Welch路线若为主要分析：t=2.338、df=37.359、P=0.025，95%CI（0.101496，1.418504）；此区间不能换成pooled区间。两法本例t相同是因为组样本量相等，不是一般结论。

### 报告示范

> 在独立观测的教学假设下，对照工艺组含量为98.50%±0.96%（n=20），新工艺组为99.26%±1.09%（n=20）。Shapiro–Wilk未发现足以拒绝正态性的证据（P均>0.05），分布形态仍需结合图形核查。Levene(mean)检验F=0.739、P=0.395，按预设课程路线采用合并方差t检验，t(38)=2.338，P=0.025；B−A均数差为0.76个百分点，95%CI为0.10～1.42。该结果达到预设α=0.05的统计学阈值；尚缺专业重要差异界值和明确药品品种标准，不能据此判断专业重要性或药典合格性。

95.0%–105.0%若用于课堂讨论，只能称“本情境预设的示意范围”，不称通用药典限度；均数比较不替代品种放行或逐片质量判断。P值是在H₀及模型假设下出现当前或更极端统计结果的概率，不是“差异由随机造成的概率”，也不衡量效应重要性。

数值来源：`output/teaching/results.json`中`tablet_assay.groups`、`levene`、`tests.pooled`与`cohens_d`；实际作业须注明自己这次输出路径。报告中的图形判断只有在实际查看图形后才可补写“未见明显偏态/异常值”。

### SPSS 读图提示

独立样本检验常见“假设等方差”（合并方差）与“不假设等方差”（Welch）两行；本题采用课程路线，Levene P=0.395时读第一行。若预设Welch，则固定读第二行；不得比较两行后挑较小P。通过增加P显示精度处理`.050`边界，保存`.sps/.spv`和含表名导出。SPSS本例尚待机房实际验证。

---

## 例题 2：配对 t（对数尺度）—— 等效界值教学演示

数据：`datasets/teaching/bioeq_cmax.csv`（24个示意对象，`subject_id`、`cmax_T`、`cmax_R`，单位ng/mL）。文件名为历史命名；现有列不含sequence、period或AUC，**不能当作完整双周期双交叉BE数据**。按ID确认唯一对象、完整对和正值，检查对象间独立的教学假设。

### 为什么先取对数

浓度数据常见右偏；本例用正值T、R的自然对数演示差值与比值的转换。检查的是ln(T)−ln(R)的分布，不能假定取对数后必然正态。预设教学界值为80.00%–125.00%；ln(0.8)与ln(1.25)关于0对称。本例使用90%CI演示区间条件，不把这一规则无条件推广到特殊品种或复杂BE设计。

### Python

```python
import json
from pathlib import Path

results = json.loads(Path("output/teaching/results.json").read_text(encoding="utf-8"))
case = results["paired_log_demo"]
print("Analysis set:", case["analysis_set"])
print("Shapiro of log differences:", case["shapiro"])
print("Paired t:", case["paired_t"])
print("GMR (%):", case["gmr_pct"])
print("90% CI (%):", case["ci90_pct"])
print("Teaching interval criterion met:", case["interval_criterion_met"])
print("Formal BE assessment:", case["formal_be_assessment"])
```

上述共同脚本先计算d=ln(T)−ln(R)，再算m=mean(d)、SE=SD(d)/√n；90%区间为`100×exp(m±t(0.95,n−1)×SE)`。`paired_t.ci95_mean_log_difference`是差值均数95%CI，`ci90_pct`是几何均值比90%CI，不能互换。GMR是各配对T/R比值的几何均值，不用原尺度算术均数比替代。

### 结果（参考答案）

- 差值Shapiro–Wilk W=0.971、P=0.682；仅表示未发现足以拒绝正态性的证据，图形与异常值仍应核查；
- 配对 t：**t(23)=−0.624，P=0.539**；
- GMR=98.10%，**90%CI（93.06%，103.41%）**；在简化配对教学模型中，区间完全进入预设界值，`interval_criterion_met=true`；
- `formal_be_assessment="not_assessed"`：无论教学区间条件是否满足，均不能据本数据作正式BE结论。

### 关键反直觉点（必讲）

P=0.539表示在所用模型下未拒绝“总体平均对数差为0”，不证明总体T、R相同或等效。若90%CI很宽，例如构造的70%–140%，应写“未能证明等效”，不能写“已证明不等效”。正式BE还须按适用指南、预设设计/统计模型及所需PK参数评价，不能只看本例一个区间。`pharm-applications/bioequivalence`尚未发布时可解释这些边界，不声称加载或完成了该流程。

### 报告示范（简化教学模型）

> 对24个示意对象的T、R正值取自然对数后作配对分析，差异检验t(23)=−0.624、P=0.539。简化模型的T/R几何均值比为98.10%，90%CI为93.06%～103.41%，满足预设80.00%～125.00%的教学区间条件。数据缺序列、周期和AUC，未作正式制剂BE评价。

数值来源：`output/teaching/results.json`中的`paired_log_demo.analysis_set`、`paired_t`、`gmr_pct`和`ci90_pct`；报告同时保留`formal_be_assessment`。实际输入改变时，区间条件及说明应随本次未舍入区间更新，不能无条件输出“满足”。

SPSS指导（未实跑）：按ID确认完整对后，计算LN(T)、LN(R)与对数差；正态性检查对数差。若做本教学区间演示，将配对分析的CI设置为90%，确认差值方向为LN(T)−LN(R)，再对区间端点取指数并乘100；另行标注所用区间，不能误读默认95%输出为90%。保存计算变量语法和结果来源。

---

## 例题 3：单样本 t —— 片重与标示值（模板）

单样本没有配套数据，给最小模板：

```python
from scipy import stats
# 20 片片重(mg)，标示平均片重 100 mg
t, p = stats.ttest_1samp(weights, popmean=100)
```

报告：“片重x̄±s=＿±＿mg（n=20），与题目给定值100mg比较，t(19)=＿，P=＿；均数差x̄−100=＿mg，均数差95%CI（＿，＿）。”本模板尚无`weights`数据、没有实际运行，也不计为完整可复跑例题。软件给出总体均数CI时，报告差值CI需两端各减100mg。
注意药典片剂重量差异检查有专属的计数式判定规则（超限片数），不是 t 检验，不要混用。
