# GitHub Copilot 安装

## VS Code / JetBrains

1. 在仓库根目录建 `.github/instructions/`（或直接用项目根的约定文件）；
2. 复制 skill 并加 `.inst.md` 后缀：

```bash
mkdir -p .github/instructions
cp skills/methods-core/t-test/SKILL.md .github/instructions/ttest.inst.md
```

3. 在 Chat/Agent 模式中用 `#ttest` 等方式引用，或在提问时附上文件。

## 简单做法

不做任何安装，把 SKILL.md 内容贴进对话首条消息，再给数据路径。Skill 是约定文本，不是插件，贴进去同样有效。
