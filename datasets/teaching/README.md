# 教学模拟数据与参考结果

三份 CSV 均为**教学模拟数据**，不含真实受试者信息。原始随机种子为 `20261017`，可由 `maintainers/data_generation/generate_datasets.py` 重新生成并逐字节复现。当前 CSV 数值自 v0.1 起未变。

## 学生怎么用

不用看任何脚本：打开对应技能的例题文件，照着里面的代码读 CSV、自己运行、把结果存进自己的 `output/`，再与本目录 `reference_outputs.txt` 核对。

- 两组含量测定 → `skills/methods-core/t-test/references/examples.md` 例题 1
- 配对对数数据 → 同文件例题 2
- 两组不良事件 → `skills/methods-core/chi-square/references/examples.md`

`reference_outputs.txt` 是冻结的参考数字，供教师核对。学生必须保留自己的本次输出，不得把参考文件当作自己的运行结果，也不得手改数字去凑参考答案。

## 三份数据

### tablet_assay.csv：两组片剂含量测定

| 变量 | 说明 |
|---|---|
| `tablet_id` | A01–A20、B01–B20 |
| `process` | `A_对照工艺`、`B_新工艺` |
| `assay_pct` | 相当于标示量的百分比，连续测量值 |

两组各 20 片。**每片独立是本模拟题的教学假设**；真实工艺比较须核对批次、抽样与实验单位，不能把同批片剂当独立工艺重复。

参考结果（基于已提交 CSV）：合并方差 t=2.338、df=38、P=0.024768；B−A=0.760 个百分点，95%CI 0.102–1.418，Cohen d=0.739。Welch 对照使用自己的自由度和 CI，报告时分别命名。本例题**不提供品种、批次放行或专业重要性标准，不判药典合格，也不直接下"无药学意义"结论**；课堂若采用 95%–105% 范围，只能明确标为题设示意范围，不得泛称现行药典统一限度。

### bioeq_cmax.csv：对数配对数据的等效界值演示

| 变量 | 说明 |
|---|---|
| `subject_id` | S01–S24；配对键 |
| `cmax_R` | 条件 R 模拟 Cmax，ng/mL |
| `cmax_T` | 条件 T 模拟 Cmax，ng/mL |

24 对数据。先验证键的唯一性，按 ID 对齐，排除缺失整对；检查对象是 ln(T)−ln(R) 差值。参考结果：配对 t=−0.624、df=23、P=0.538838；GMR=98.10%，90%CI 93.06%–103.41%。区间落入本题预设 80.00%–125.00% 的教学界值，但**差异检验 P>0.05 不证明等效**。

**本数据没有序列、周期或完整 PK 参数，不是正式交叉 BE 分析数据。** 区间越界应说"未能证明等效"，不能据此直接证明不等效。正式 BE 方法与特殊品种规则须另行学习和核查。

### adverse_events.csv：两组不良事件记录

| 变量 | 说明 |
|---|---|
| `subject_id` | PA001–PA120、PB001–PB120 |
| `drug` | `A药`、`B药` |
| `adverse_event` | 1=发生，0=未发生；未知编码须报错，缺失须记录排除数 |

A药 24/120（20.0%），B药 8/120（6.7%）；n=240，理论频数为 16、104、16、104。本题课程链选 Pearson χ²=9.231、df=1、P=0.002380；Yates 与 Fisher 作为明确标识的对照。

事件优先表（行 A药/B药，列 发生/未发生）为 `[[24,96],[8,112]]`，样本 OR=3.50，log-Wald 95%CI 1.503–8.151；RD=13.3 个百分点，Wald 95%CI 4.9–21.8。样本 OR/log-Wald 与 R `fisher.test` 的条件 MLE/条件精确区间不是同一算法，报告时分别命名。结论限于观察关联，不能解释为已控制混杂或已证明因果。

课程条件链（独立 2×2）：先排除退化表，再按 n<40 或 Tmin<1 选 Fisher 双侧，否则 Tmin<5 选 Yates，其余选 Pearson。R×C、配对表和调整分析另判。孤立零格或稀疏表不硬给 Wald 区间（禁止加 0.5 硬凑），写"未估计该区间"并说明原因。

## 维护者：重新生成数据

生成与分析分离。生成脚本不计算参考答案，默认写到独立目录，目标文件已存在时拒绝覆盖（明确需要时加 `--overwrite`）。

```bash
python maintainers/data_generation/generate_datasets.py --output-dir /tmp/teaching-generated
python maintainers/scripts/analyze_teaching.py --data-dir /tmp/teaching-generated --output-dir /tmp/generated-analysis --t-policy course
```

维护参考答案时，先核验 CSV、方法、方向和实际输出，再把核验后的 `summary.txt` 同步为 `reference_outputs.txt`，不得手改统计数字。原始 CSV 保持只读。新数据需记录生成逻辑、种子、变量、设计假设及许可；不接收真实受试者级数据。
