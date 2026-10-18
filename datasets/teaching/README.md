# 教学模拟数据与参考结果

三份CSV均为**教学模拟数据**，不含真实受试者信息。原始种子为`20261017`；在`requirements-teaching.txt`所列依赖版本下可重现数据值。当前CSV数值保持v0.1不变；末尾空行不影响读取，不承诺不同文件格式或依赖版本的字节完全相同。

## 先分析现有数据

在仓库根目录运行一条软件路线即可。下面的Python流程已实际运行；基础R另有WebAssembly数值与模板验收，桌面R和SPSS仍须在所用环境核验，不能据此视为三轨全部通过。

```bash
python -m pip install -r requirements-teaching.txt
python scripts/analyze_teaching.py --output-dir output/teaching --t-policy course
python -m unittest discover -s tests -v
```

`course`为本示范预设的课程规则：Levene采用`center=mean`，用未舍入P判断，P≤.05选Welch，其余选pooled。另支持事先指定`--t-policy welch`，固定以Welch为主；不得看P后选择策略。Shapiro和Levene的非拒绝均不证明分布或方差假设成立，须结合设计、图形、异常值和各组样本量。

分析脚本只读CSV，不重新生成数据；输出：

每轮输出目录须尚不存在，已有空目录也拒绝。重跑时将`--output-dir`改为新名称，并同步下游读取路径；原有结果保留供溯源。此规则保护共用Python分析命令，不代表其他软件的保存命令自动具备同样保护。

| 文件 | 内容 |
|---|---|
| `results.json` | 完整精度的分析集、方法、方向、检验、效应、CI、输入SHA-256、软件版本和实际执行状态 |
| `summary.csv` | `field,value`表，每个字段直接对应JSON路径，便于核对报告数字 |
| `summary.txt` | 本次结果的可读摘要 |
| `adverse_events_table.csv` | 带标签的事件优先列联表，固定行A药/B药、列发生/未发生 |
| `diagnostics.png` | 两组含量数据、完整配对对数差值的正态Q–Q图；须人工查看 |
| `diagnostic_points.csv` | 每点的样本、标识、秩、观测值、标准正态分位数和参考线值，与分析排除规则一致 |

`reference_outputs.txt`是上述分析脚本实际输出的冻结摘要，供教师核对。学生须保留自己的本次输出，不得把参考文件当作自己的运行结果。JSON根键为`metadata`、`tablet_assay`、`paired_log_demo`、`adverse_events`、`mcnemar_demo`、`diagnostics`；McNemar来自例题中的明确汇总表，不冒充个体CSV。

Q–Q图以`(秩−0.5)/n`为绘图位置、标准正态分位数为横轴；参考线为样本均数加样本SD乘横轴值。不同软件绘图位置和参考线可能不同，不逐像素比图。先看整体弯曲、两端偏离和孤立点，再结合样本量与数据来源判断；小样本不贴线本身不构成拒绝正态的阈值。`diagnostics.review_status=requires_human_review`表示输出未记录人工结论，不自动判正态或切换检验；学生查看后把判断写进`DECISIONS.md`。

## 三份数据的范围

### tablet_assay.csv：两组片剂含量测定

| 变量 | 说明 |
|---|---|
| `tablet_id` | A01–A20、B01–B20 |
| `process` | `A_对照工艺`、`B_新工艺` |
| `assay_pct` | 相当于标示量的百分比，连续测量值 |

两组各20片。**每片独立是本模拟题的教学假设**；真实工艺比较须核对批次、抽样与实验单位，不能把同批片剂当独立工艺重复。

基于已提交CSV：pooled t=2.338、df=38、P=0.024768；B−A=0.760个百分点，95%CI为0.102～1.418，Cohen d=0.739。Welch对照使用自己的自由度和CI，输出中分别命名。结果不提供品种、批次放行或专业重要性标准，**不判药典合格，也不直接下“无药学意义”结论**。如课堂采用95%～105%范围，只能明确标为题设示意范围，不得泛称现行药典统一限度。

### bioeq_cmax.csv：对数配对数据的等效界值演示

| 变量 | 说明 |
|---|---|
| `subject_id` | S01–S24；配对键 |
| `cmax_R` | 条件R模拟Cmax，ng/mL |
| `cmax_T` | 条件T模拟Cmax，ng/mL |

24对数据。先验证键的唯一性，按ID对齐，排除缺失整对；检查对象是ln(T)−ln(R)差值。本例配对t=−0.624、df=23、P=0.538838；GMR=98.10%，90%CI为93.06%～103.41%。区间满足本题预设80.00%～125.00%的教学条件，但差异检验P>.05不证明等效。

**本数据没有序列、周期或完整PK参数，不是正式交叉BE分析数据。** 输出`interval_criterion_met`随实际区间改变，`formal_be_assessment`始终为`not_assessed`。区间越界应说“未能证明等效”，不能据此直接证明不等效。正式BE方法与特殊品种规则须另行学习和核查。

### adverse_events.csv：两组不良事件记录

| 变量 | 说明 |
|---|---|
| `subject_id` | PA001–PA120、PB001–PB120 |
| `drug` | `A药`、`B药` |
| `adverse_event` | 1=发生，0=未发生；未知编码须报错，缺失须记录排除数 |

A药24/120（20.0%），B药8/120（6.7%）；n=240，理论频数为16、104、16、104。本题课程链选择Pearson χ²=9.231、df=1、P=0.002380；Yates和Fisher作为明确标识的对照。

事件优先表为`[[24,96],[8,112]]`，样本OR=3.50，log-Wald 95%CI为1.503～8.151；RD=13.3个百分点，Wald 95%CI为4.9～21.8。CI使用z=1.96以保持示例统一；它们不等同于Fisher条件OR/精确CI。结论限于观察关联，不能解释为已控制混杂或已证明因果。

课程条件链仅限独立2×2：先处理退化表，再按n<40或Tmin<1选Fisher双侧，否则Tmin<5选Yates，其余选Pearson。R×C、配对表和调整分析另判。空行/列边际本实现仅描述；个别零格保留可用检验，但不偷加0.5，不硬给Wald OR区间。本最小实现对零格或Tmin<5均不估计OR和RD的Wald区间，保留可定义的点估计并标明未实现适当稀疏区间算法；这是本实现的保守范围，不是所有区间方法的通用阈值，也不要求不同算法的P与CI必然一致。零样本组的率写null而非0%。

## 维护者重新生成数据

生成与分析现已分开。生成脚本不计算或改写参考答案，默认写到独立目录；已有目标文件时拒绝覆盖，维护者明确需要时才加`--overwrite`。

```bash
python datasets/teaching/generate_datasets.py --output-dir output/teaching-generated
python scripts/analyze_teaching.py --data-dir output/teaching-generated --output-dir output/generated-analysis --t-policy course
```

维护参考答案时，先核验CSV、方法、方向和实际输出，再把核验后的`summary.txt`同步为`reference_outputs.txt`；不得手改统计数字。原始CSV保留只读。新数据需记录生成逻辑、种子、变量、设计假设及许可；真实数据仅接受许可清晰且不含个体信息的公开汇总数据，不接收真实受试者级数据，即使其已经公开。
