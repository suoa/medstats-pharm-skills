# Claude Code 安装

Claude Code 会自动读取项目中的技能约定。

1. 把需要的 skill 目录复制到项目约定目录：

```bash
mkdir -p .claude/skills
cp -r skills/reporting/method-selection-router .claude/skills/
cp -r skills/methods-core/t-test .claude/skills/
cp -r skills/methods-core/chi-square .claude/skills/
```

2. 也可以复制到用户级目录对所有项目生效：`~/.claude/skills/`；
3. 在项目根目录启动 Claude Code，直接描述分析任务，它会先匹配 method-selection-router；
4. 第一次使用建议带上学生项目模板：

```bash
cp -r templates/student-project/* 你的项目目录/
```

需要全部 skill 时整目录复制即可，但按需加载更省上下文。
