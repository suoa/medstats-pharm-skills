# 安装方式

Skill 本质是 Markdown 约定，不绑定某个软件。下面给出几种常见用法，按你的工具选一个。

## 方式 A：直接给 agent 读（零配置，推荐学生先用）

1. 下载本仓库；
2. 只把本次要用的 skill 文件夹复制出来，例如 `skills/methods-core/t-test/`；
3. 对 agent 说：「读取这个 SKILL.md，按它的约定帮我分析数据」，或直接把 SKILL.md 内容粘贴进对话框；
4. 把数据放在 [templates/student-project](../templates/student-project) 建好的目录里。

## 方式 B：按工具安装到技能目录

- Claude Code（本地）：见 [claude-code.md](claude-code.md)
- Cursor：见 [cursor.md](cursor.md)
- GitHub Copilot：见 [github-copilot.md](github-copilot.md)
- 扣子（Coze）等平台型 agent：把 SKILL.md 作为「技能/知识库/提示词」内容导入，参考 [general-md.md](general-md.md)
- 其他 agent：只要支持自定义指令或技能文档，方式都一样——把 skill 目录放进它读取约定文件的位置

## 方式 C：只看不用装

直接在 GitHub/Gitee 上读 SKILL.md，照着步骤手动操作 SPSS/R/Python 也可以，skill 的价值在约定本身。

## 下载慢 / 打不开 GitHub

用 Gitee 镜像，见 [gitee.md](gitee.md)。

## Python 环境（可选）

只有打算跑 Python 分析时才需要：

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install numpy pandas scipy statsmodels
```

SPSS 和 R 用户不需要 Python。
