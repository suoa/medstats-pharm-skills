# SPSS机房验收包：待实机运行

此包只覆盖仓库当前三份合成CSV和一张配对汇总表，供教师先在机房验证。**没有SPSS实跑结果或截图**；参考数字由Python实际复算，不是SPSS输出。模板依据IBM官方命令资料编写，语法、许可及表头仍须在所用SPSS版本核查。

## 学生或教师使用已生成的包

1. 每轮验收完整解压到一个新的目录，保留`datasets/teaching/`和空的`output/`目录；开跑前确认`output/`为空。重跑须再复制一份新包目录并重新设置路径，不能直接覆盖上一轮。SPSS的`OUTPUT SAVE`会无提示覆盖同名SPV，生成器的拒绝覆盖规则不保护SPSS实跑文件。包内带原始CSV的逐字节副本，无须安装Python或R。
2. 保存已有工作，开启新的SPSS Unicode会话。不要在有未保存数据的会话中运行：`GET DATA`或`DATA LIST`可能替换未命名活动数据集。本语法不会清空/关闭其他数据集，但不提供当前会话的自动备份。
3. 打开`00_setup.sps`，把`__EDIT_PACK_ROOT__`改成解压后包根目录的绝对路径，例如`C:/teaching/spss-check`。运行该文件；`CD`报错立即停止。后续四份语法保留`CD '.'`，在同一会话从当前包目录读写。
4. 按需要打开`01`～`04`语法。**先从Section 1标题选到STOP前的最后一条命令运行**，核对ID、重复/缺失/编码标志、组别和总数，再选Section 2。Section 1包含新建Viewer、软件版本与小数点设置，不能只从GET DATA开始选。注释中的STOP是人工闸门，不会自动阻止“全部运行”；有异常必须停止。不要将模板直接用于学生自带或真实数据。
5. 查看Q–Q图、表头和脚注，保存本次`.sps`、真实`.spv`及PDF。每份任务建立独立Viewer并写到包内`output/`。若保存或PDF导出失败，记录错误并手动保存本次Viewer，不能从参考文件补产物。
6. 对照`reference_values.csv`填写`SPSS_run_record.csv`的实测值及单位、运行日期、软件版本、输出文件、表名及行列。率差使用比例或百分点时必须注明换算；两组含量均值是标示量百分比，均数差以百分点计。初始`not_run`不代表通过；已运行但尚未核数字可写`run_unchecked`，实际核对后写`matched`、`mismatch`、`not_shown`或`not_applicable`并说明原因。参考文件不得复制到实测列冒充验收。

目录中若没有生成的`00_setup.sps`或参考表，说明拿到的是仓库源码模板，应先由维护者执行文末生成命令。

## 四项任务核对重点

| 文件 | 输入及方向 | 必查输出 |
|---|---|---|
| `01_tablet_assay.sps` | A/B两组含量；组1=B、组2=A | 各20例；均数/SD；Levene的Based on Mean；预定pooled/Welch行的t、df、P及对应95%CI；差值为B−A |
| `02_paired_log_demo.sps` | 24个唯一完整对；ln(T)−ln(R) | 检查差值分布；CI90与CI95分别标示；LIST中GMR及反变换90%CI，不把对数区间直接当百分比区间 |
| `03_adverse_events.sps` | 行A/B，列发生/未发生 | 两组分母、事件优先表、理论频数及主要Pearson；OR方向；由实际计数算的OR/RD及明示z=1.96的Wald区间 |
| `04_mcnemar.sps` | 同一对象配对汇总；频数加权 | 完整表N=120；精确二项只用b=18、c=6，N=24；读取双侧精确P；结束时关闭加权 |

主要方法须事先确定，不从几个P中挑最小值。`required`为本题必核数值，`comparison`为具名算法对照，`if_shown`为本机显示时核对，`reference_only`只作教学参考。未显示的渐近χ²不能填入精确检验结果。保留足够精度再比较；三位显示的差异应先查舍入与算法，不直接判错。P<.001时按报告规范写P<.001，不写P=0.000。

本包显式以1.96计算OR/RD的Wald区间；SPSS原生Risk Estimate区间可能采用更精确的正态分位数或其他实现。先硬核OR点估计与方向，再注明区间算法；不强求原生区间最后一位等于公式区间。小样本Shapiro不拒绝不证明正态，Q–Q图也不能证明独立性。

## 跨版本及许可

- 语法导入前显式运行`SET DECIMAL DOT`，并用`SHOW DECIMAL`记录设置；本包CSV使用点小数，Unicode模式不保证小数标记一致。

- 独立t的新版本可能需另开方差齐性输出，故另运行`ONEWAY ... /STATISTICS HOMOGENEITY`，读取Based on Mean。这里出现的ANOVA表不是本题新增的主要检验。
- 独立2×2的`CROSSTABS /STATISTICS=CHISQ`可带Fisher/Yates。IBM命令参考和GUI说明对Fisher自动显示条件的表述有差异；本机未显示则写`not_shown`，不得复制参考P冒充本机结果。当前稠密例的主要方法仍为Pearson。
- 默认语法不请求`/METHOD=EXACT`。该选项有平台和附加许可条件，不能要求所有机房安装。IBM的`NPAR TESTS MCNEMAR`文档写不一致对子数<25时用二项分布，与课程m<40分界不同；m在25～39时不能假定自动输出课程要求的精确P。本题用`NPAR TESTS /BINOMIAL(.5)`对不一致对子做明确双侧二项复核，不依赖McNemar自动阈值。
- 当前语法面向桌面SPSS 25以上的候选流程，未实机覆盖25/26/27等版本。`OUTPUT SAVE/EXPORT`不是SPSS Server Batch Facility的通用保存方案。

## 维护者生成与核对

从仓库根目录运行，目标目录和ZIP均须不存在；生成器拒绝覆盖已有机房结果：

```bash
python scripts/build_spss_check.py --output-dir output/spss-check
```

生成器读取现有CSV并重新计算参考值，复制三份CSV、渲染四份语法、写出独立参考JSON/CSV、空白运行记录及SHA-256清单，另生成同名ZIP。不会生成SPV/PDF，不修改原始CSV，也不把模板静态检查算作SPSS通过。输出目录可改用另一个新名称；课程数据或公式变更后须重新验收。

## IBM官方查证入口

- [GET DATA的数值格式与小数标记](https://www.ibm.com/docs/en/spss-statistics/32.0.0?topic=stgdc-variable-format-specifications-type-txt-get-data-command)
- [GET DATA及UTF8](https://www.ibm.com/docs/en/spss-statistics/30.0.0?topic=reference-get-data)
- [ONEWAY统计量](https://www.ibm.com/docs/en/spss-statistics/31.0.0?topic=oneway-statistics-subcommand-command)
- [CROSSTABS统计量](https://www.ibm.com/docs/en/spss-statistics/32.0.0?topic=crosstabs-statistics-subcommand-command)
- [NPAR TESTS的BINOMIAL](https://www.ibm.com/docs/en/spss-statistics/30.0.0?topic=tests-binomial-subcommand-npar-command)
- [NPAR TESTS的McNemar自动规则](https://www.ibm.com/docs/en/spss-statistics/30.0.0?topic=tests-mcnemar-subcommand-npar-command)
- [OUTPUT SAVE](https://www.ibm.com/docs/en/spss-statistics/30.0.0?topic=reference-output-save)及[PDF导出](https://www.ibm.com/docs/en/spss-statistics/30.0.0?topic=export-pdf-subcommand-output-command)

部分IBM页面本轮直接访问返回403，查证使用官方搜索索引的命令正文交叉核对；未据此声称完成SPSS软件解析或运行。
