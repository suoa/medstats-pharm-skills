# 变更记录

本文件记录已发布版本。维护者工程脚本、测试与验收记录见本目录；学生只需阅读 `skills/`、`datasets/`、`templates/student-project/`。

## v0.1.1 — 2026-10-18（统计口径修订；学生面代码保持透明）

外部评审（GPT/Codex，PR #1）发现的统计口径问题，经维护者独立复算后采纳其修正；工程化产物经拆分后归入 `maintainers/`，不进入学生路径。三份教学 CSV 数值未变，历史参考答案口径不变。

统计修正（skills/ 面向学生）：
- 修正独立四格表示例的 OR 方向：`pd.crosstab` 默认列按 0,1 排列，会让 `fisher_exact` 的比值比方向与正文相反（本例双侧 P 恰好相同，此前未暴露）。统一为"行[A药,B药]、列[发生1,未发生0]"的事件优先排列，OR=3.50（95%CI 1.50–8.15）。
- 正态性表述改为"Shapiro–Wilk 非拒绝不证明正态"，要求结合 Q–Q 图与异常值；配对 t 检验改查差值的正态性。
- 明确 Levene 的中心定义（mean=经典 Levene；median=Brown–Forsythe，SPSS 与 car 包默认），课程路线用 mean；合并方差/Welch 必须在看结果前预设。
- 含量测定例题不再对品种未知的产物套用具体药典限度，专业意义标 not_assessed；BE 对数尺度例题限定为"教学区间演示"，不宣称完整生物等效性评价（数据无 sequence/period/AUC）。
- 卡方补退化表、孤立零格、配对键对齐的处理纪律：稀疏表不硬套 Wald 区间（禁止加 0.5），Fisher/McNemar 精确法不强填 χ²/df，McNemar 不一致对子 b+c<40 用精确二项。
- router 补设计分支、"SW 非拒绝不是正态合格证"、能力边界（真实数据、效应方向、处方决策均不由代理判定）。

工程结构（maintainers/ 面向维护者）：
- 教学分析脚本、数据生成脚本、SPSS 机房验收包生成器、基础 R 复核脚本及 28 项测试统一移入 `maintainers/`，补 `__init__.py` 修复第三方包名遮蔽导致的测试收集失败。
- 学生示例代码保持直白：Python 直接用 scipy/statsmodels 读 CSV 计算并保存；R 用 `t.test`/`chisq.test`/`fisher.test`/`binom.test`，不引入包装器。
- SPSS 四份语法与参考值打包器保留在 `maintainers/spss_pack/`，**尚未在 SPSS 实机执行**；记录见 `maintainers/qa/spss-machine-check.md`。
- 桌面 R 的 `test_R_templates.R` 在本环境（无 Rscript）未运行；此前 WebR 0.6.0/R 4.6.0 的 99 字段交叉复核为评审方记录，见 `maintainers/qa/validation.md`。

## v0.1 — 2026-10-17

- 发布 router、t-test、chi-square 三项示范技能、三份合成数据、学生模板与安装说明。
- 代码使用 MIT，内容使用 CC BY 4.0。
