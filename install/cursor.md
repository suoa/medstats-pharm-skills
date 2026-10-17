# Cursor 安装

Cursor 通过项目规则文件读取约定。

1. 在项目根目录建 `.cursor/rules/`；
2. 把要用的 `SKILL.md` 复制进去并改名，例如：

```bash
mkdir -p .cursor/rules
cp skills/methods-core/t-test/SKILL.md .cursor/rules/ttest.mdc
```

3. 在文件头部加一行让 Cursor 按需触发（也可手动 @ 引用）：

```
description: t检验（单样本/配对/独立样本）的方法约定与验证闸门
globs: *.csv,*.sav,*.R,*.py
```

4. method-selection-router 建议设为全局规则（放在 `~/.cursor/rules/`），让它在每个统计任务开始时生效。

另一种更简单的用法：打开项目后在 Chat 中直接附上 SKILL.md 并说明「按此约定执行」。
