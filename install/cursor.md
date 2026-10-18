# Cursor 安装

使用Cursor原生Agent Skills目录，不把`SKILL.md`改名为规则文件。以下从本仓库根目录运行，安装到当前项目；其他项目请替换目标路径。Windows也可手动复制完整目录。

```bash
mkdir -p .cursor/skills
cp -R skills/reporting/method-selection-router .cursor/skills/
cp -R skills/methods-core/t-test .cursor/skills/
cp -R skills/methods-core/chi-square .cursor/skills/
```

应得到`.cursor/skills/t-test/SKILL.md`及`references/`。个人本机skill目录可用`~/.cursor/skills/`；云端可用范围依客户端设置，不假设自动同步。本说明不使用`~/.cursor/rules/`作为全局安装路径。

在客户端技能列表中核对已发现的skill，再要求“先读取method-selection-router，再按题目读取方法及必要references”。原生skills与`.mdc`规则是不同形式，不能只换后缀；`ttest.inst.md`也不是本安装方法。

例题CSV仍在仓库`datasets/teaching/`，不随单个方法目录出现。独立作业使用[学生项目模板](../templates/student-project/README.md)，按真实位置调整数据路径。只附Markdown时按[通用方式](general-md.md)使用，并核实执行/保存能力。

核查状态（2026-10-18）：目录已按[Cursor官方Skills文档](https://cursor.com/docs/skills)静态核对；本次未实际启动Cursor，自动触发与软件运行仍待本机验证。
