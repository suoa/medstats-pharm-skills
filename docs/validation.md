# v0.2 限定教学试用验证记录

日期：2026-10-18。修订基线：`9fe0a2705db79c9067ebd9ed3f8d2a03d2620f4c`。当前为未发布候选，不能把这一记录推广为所有软件、数据或设计已验证。

## 实际运行

以下命令从仓库根目录运行。分析脚本只读取现有 CSV；数据生成在隔离临时目录另验，不在学生分析时重建数据。

```bash
python scripts/analyze_teaching.py --output-dir output/teaching --t-policy course
python -m unittest discover -s tests -v
```

Python 基线：Python 3.12.14、NumPy 2.3.5、pandas 2.2.3、SciPy 1.17.0。具体依赖与实际输出中的版本信息一起核对；最新在线文档版本可能高于本轮实跑版本。

还创建了复用系统预装包的独立 venv，实际执行 `python -m pip install -r requirements-teaching.txt` 成功（新增安装statsmodels 0.15.0等依赖），随后在该环境运行分析命令和全部19项测试均通过。此验收覆盖当前运行环境，不代表所有操作系统或完全空白环境均安装通过。

上述命令已执行通过：**20项 unittest（18项数值/边界、2项技能分发检查）**。另运行 `--t-policy welch`，结果正常保存到独立目录；三个技能均通过 skill-creator 的 `quick_validate.py` 格式核验，`git diff --check` 通过。三份原始 CSV 相对基线的字节未变；固定种子重建在临时目录逐表比较通过，不要求尾空行等格式字节相同。

| 复算项 | 本次结果 | 方法与方向 |
|---|---|---|
| 含量均数差 | 0.760000 个百分点；95%CI 0.101866621～1.418133379 | B−A，pooled |
| 含量主要检验 | t=2.337732158，df=38，P=.0247676045 | 课程Levene(mean)路线，Levene P=.3954279325 |
| Welch 对照 | df=37.359337924，P=.0248629773；95%CI .101495789～1.418504211 | 事先选择Welch时使用对应区间 |
| 配对对数演示 | t=−.623891536，P=.5388380307；GMR=98.097725707%，90%CI 93.056237575%～103.412345477% | ln(T)−ln(R)，24完整对；正式BE未评估 |
| 不良事件主要检验 | χ²=9.230769231，df=1，P=.0023798165 | 未校正Pearson，事件优先表 |
| Fisher 对照 | 双侧P=.0038347022 | 概率排序定义；不填χ²/df |
| OR 与比例差 | OR=3.50，95%CI 1.502954231～8.150614137；RD=.133333333，95%CI .048988363～.217678304 | A相对B；log-Wald和独立比例Wald，z=1.96 |
| McNemar | 精确P=.0226558447；校正渐近P=.0247446720；未校正P=.0143058784 | b=18、c=6，各方法分开命名 |

实际产物为 `output/teaching/results.json`、`summary.csv`、`summary.txt`、`adverse_events_table.csv`；参考输出由本次摘要同步。原始输入路径/哈希、版本、分析集、方向和方法标签在 JSON 中；运行产物不作为公共教学原始数据提交。

零边际/零样本组、孤立零格、未知编码、配对重排/缺失/重复键、临界期望频数、未舍入`.050`分支、预设Welch遇不可定义Levene、界值越界后的动态说明均有实际测试。固定Welch不因Levene不可计算而停止；课程分流无法判断时仍须报错核查。稀疏/边界比例没有实现适当区间时保留点估计并明确未估计，不补造端点。

发布前独立复查发现并修正一处例题文字：`[[0,20],[4,16]]` 的 n=40、Tmin=2，按本课程链主要方法为 Yates（χ²=2.5，P=.1138462980），Fisher 双侧 P=.1060291060 仅作对照。实际脚本原已选 Yates；本次直接调用复算确认，未修改算法。

同轮复查还发现恒定比值 T=[2,4,6]、R=[1,2,3] 经对数相减会产生约10⁻¹⁶量级的舍入变异，绕过原有`SD==0`保护。现按对数数值尺度与机器精度判断不可分辨变异并拒绝该退化t分析；新增测试同时检查恒定比值被拒和接近1的可分辨小变异仍可分析。参考数据的复算结果不变，当前20项测试全部通过。

statsmodels 0.15.0 另在本地隔离依赖目录通过 `PYTHONPATH` 加载，实际运行 `mcnemar([[42,18],[6,54]], exact=True)` 及两种渐近参数，P值与表中三项一致。共享脚本使用SciPy `binomtest`，无需在默认环境导入statsmodels。此处仅比较这张表，不宣称不同实现的每个边界处理完全相同。

两个完整例题的 Python 读取块在 course/Welch 输出下联调通过；单样本无数据模板未执行。**未生成或查看Q-Q图，本轮不声称t检验的图形前提核验已完成**；数值复算不代替学生/教师对设计与分布的判断。

八个边界案例另由两个不继承评审上下文的新任务代理单轮作答，八项达到选法/缺项/执行诚实边界；原始回复见 [转录](router-trial-transcript.md)。完整目录复制命令在隔离目录执行通过。均未据此宣称真实客户端自动触发、多轮分析或课堂效果已验证。

## 已定教学口径

- 含量：课程路线采用基于均值的 Levene，未舍入 P≤.05 选 Welch，否则选 pooled；另可事先选择固定 Welch 路线。比较方向 B−A，不按检验结果中较小的 P 挑策略。
- 不良事件：行按 A药、B药，列按发生、未发生；主要方法按课程独立四格表条件链选择，OR 表示 A 相对 B 的事件优势比，率差为 A−B。OR 与率差的 Wald 区间算法分别标明；其他算法不强求相同端点。
- 配对 Cmax：先按受试者键对齐，演示 ln(T)−ln(R)、GMR 及 90% CI 与 80%–125% 教学界值；`formal_be_assessment` 保持 `not_assessed`。该文件缺少序列、周期、AUC，不能作正式交叉 BE 判定。
- McNemar：课堂采用不一致对数 b+c<40 时精确二项；这是一项预定教学规则，不是普遍适用的数学分界。精确与渐近输出分别标示。

## 尚未执行或待核

| 项目 | 状态与要求 |
|---|---|
| R 4.x 实跑 | 本轮环境无 Rscript；代码经官方文档核对，仍待 R 环境执行、保存结果并核对 CI/方法标签 |
| SPSS 25 以上实机 | 本轮无 SPSS；菜单、精确检验入口与实际输出须在课程机位核查，不能宣称跨版本默认值一致 |
| 国内教材口径 | 任课教师需填写所用人卫版《医学统计学》的具体版次、相关规则和本课取舍；本轮未取得可逐字核验的教材全文，不编页码或声称已完成教材一致性认证 |
| 真实课堂 | 尚未完成学生试用；自动数值测试、文档静态检查与模型任务试验均不能代替课堂验收 |
| 正式 BE | 未执行；须另行按适用规范和设计分析，当前数据不能通过补写虚构字段满足要求 |

## 依据与适用边界

- [SciPy Levene](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.levene.html)：mean 与 median 是不同中心定义；本仓库显式指定参数，避免软件默认值混用。
- [R McNemar](https://stat.ethz.ch/R-manual/R-devel/library/stats/html/mcnemar.test.html) 与 [statsmodels McNemar](https://www.statsmodels.org/stable/generated/statsmodels.stats.contingency_tables.mcnemar.html)：R 的 `mcnemar.test` 为渐近卡方实现；精确分支使用 `binom.test`，Python 显式设置 `exact`。
- [国家药监局 M13A 适用公告（2026年第49号，政府转载）](https://www.hunan.gov.cn/zqt/zcsd/202605/t20260521_33982465.html)与 [ICH M13A（FDA 发布的最终文本）](https://www.fda.gov/media/165049/download)：常规速释口服制剂 BE 有设计、参数及适用范围要求；80%–125% 不能无条件用于所有药物或设计。公告还规定既有方案的过渡安排，正式任务须按具体适用日期核查。
- [《中国药典》2025 年版四部增修订概况](https://www.cnpharm.com/c/2025-07-18/1076142.shtml)：旧 9011、9012 已删除，贡献指南不再以“2025 年版四部 9012”作现行引用示例。本例也不提供具体品种含量质量标准。
- 原生技能目录参照 [GitHub Copilot](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)、[Cursor](https://cursor.com/docs/skills)、[Claude Code](https://code.claude.com/docs/en/skills) 官方说明；仅核查目录格式，不等于在这些平台完成了实际安装与触发测试。
