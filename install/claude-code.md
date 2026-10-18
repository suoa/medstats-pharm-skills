# Claude Code 安装

使用原生skill目录，完整保留每个方法的`references/`。以下命令从本仓库根目录运行，安装到当前项目；作业在其他项目时，把目标目录换为该项目路径。命令供具备`mkdir`和`cp`的终端使用，Windows也可用文件管理器复制同样的完整目录。

```bash
mkdir -p .claude/skills
cp -R skills/reporting/method-selection-router .claude/skills/
cp -R skills/methods-core/t-test .claude/skills/
cp -R skills/methods-core/chi-square .claude/skills/
```

项目级结果应为`.claude/skills/t-test/SKILL.md`及其`references/`等。个人本机目录可用`~/.claude/skills/<name>/`；不假设本机个人安装会自动同步到云端。

启动后明确请求“先读取method-selection-router，再根据题目读取对应方法及需要的references”；自动发现不保证调用顺序。通过客户端的skill列表/读取记录检查实际加载，不只看agent口头声称。

数据与学生模板不在方法skill内部：保留仓库`datasets/teaching/`以运行仓库例题，或把教师数据放实际项目`data/raw/`并调整路径；模板见[学生项目说明](../templates/student-project/README.md)。方法未发布时可以一般答疑，但不假装调用。

核查状态（2026-10-18）：目录规则已按[Claude Code官方文档](https://code.claude.com/docs/en/skills)静态核对；本次未实际启动Claude Code，自动触发、代码执行与文件保存须在所用客户端另验。仅贴文档不授予这些能力。
