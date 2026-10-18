# 安装与开始使用

Skill是给agent读取的步骤与约定；安装Markdown不会自动提供统计软件、数据读取、代码执行或文件保存能力。单份作业只选教师指定或事先选定的一轨，不必同时安装三套统计软件。

## 方式A：先读取本次材料

1. 下载本仓库，或取得教师发放的作业包；数据仍使用教师指定文件。
2. 向agent提供`method-selection-router`、本次方法的完整目录（`SKILL.md`及`references/`）和题目。只粘主文件时，应另附本题需要的参考材料；不宣称已读未提供的文件。
3. 按[学生项目模板](../templates/student-project/README.md)保存原始数据；仓库例题路径以仓库根目录为基准，独立作业须改为实际数据路径。
4. 用三行开始，已有信息不重填：

```text
题目：我想知道……（也可粘贴原题）
数据：附件或路径；是否同一对象测过多次？不清楚可以说明
要求：软件与教师规定；未指定可说明
```

## 方式B：使用工具原生技能目录

- [Claude Code](claude-code.md)：`.claude/skills/<name>/SKILL.md`
- [Cursor](cursor.md)：`.cursor/skills/<name>/SKILL.md`
- [GitHub Copilot](github-copilot.md)：`.github/skills/<name>/SKILL.md`
- [通用对话/知识库](general-md.md)：作为指令与参考资料输入，能力须另行确认。

完整复制每个含`SKILL.md`的技能目录，保留`references/`；不要仅改文件后缀，也不要把分类目录当作单个skill。自动匹配不保证先调用router；首次可明确说“先读取method-selection-router，再按题目读取方法与必要references”，并检查实际读取情况。

## 方式C：按文档手动操作

可以只读文档，手动操作SPSS/R/Python。SPSS路线用“粘贴”留`.sps`，保存`.spv`与可读导出。数字允许准确转录并标表名/行列，不能以例题答案代替本次输出。

## 下载渠道

GitHub源仓库：[suoa/medstats-pharm-skills](https://github.com/suoa/medstats-pharm-skills)。Gitee镜像[筹备中](gitee.md)，当前不提供可用镜像地址。

## Python（选用时）

Python用户可先建独立环境，在仓库根目录用该环境的`python -m pip install -r requirements-teaching.txt`安装本轮核验的依赖；记录实际Python及包版本。基线为Python3.12，其他环境须重新验收。当前R模板的mean中心Levene用基础`stats`实现，无需`car`；若自己改用`car::leveneTest`，须另装该包并固定中心算法。SPSS和R用户无需为此安装Python。R的WebAssembly实跑不等于桌面安装验收；客户端安装成功、代码实跑、输出保存与数值核验须分别记录，不以阅读文档代替通过。

共用Python分析脚本每轮使用一个尚不存在的`--output-dir`，已有空目录也拒绝写入；重跑改用新目录，并同步结果读取路径。原生R/SPSS各自按已验收的保存步骤操作，这个保护只覆盖共用Python分析命令。

## 无执行或保存能力时

仅能读文档时给标为“未执行”的指导；能运行不能保存时可展示真实输出，注明“已计算，尚未保存，未完成作业文件验收”。规划中的方法仍可普通答疑，不伪称其仓库流程已加载、实跑或验证。
