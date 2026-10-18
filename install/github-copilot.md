# GitHub Copilot 安装

在支持Agent Skills的Copilot客户端使用原生技能目录。以下命令从本仓库根目录运行，安装到当前项目；其他项目请替换目标路径。Windows也可手动复制完整目录。

```bash
mkdir -p .github/skills
cp -R skills/reporting/method-selection-router .github/skills/
cp -R skills/methods-core/t-test .github/skills/
cp -R skills/methods-core/chi-square .github/skills/
```

应得到`.github/skills/t-test/SKILL.md`及`references/`。检查当前客户端实际识别的skills，再请求先读router、后读方法及必要参考材料；不依靠未经验证的`#ttest`别名保证加载。

这里使用Agent Skills，不能把主文件改成`.inst.md`当作已安装。若另需路径专属自定义指令，其官方形式是`.github/instructions/NAME.instructions.md`并带`applyTo`；这与完整方法skill的安装不同，无需为本次作业同时配置。

例题数据需保留`datasets/teaching/`或另放真实作业路径；使用[学生项目模板](../templates/student-project/README.md)。客户端只支持附文件时，可走[通用方式](general-md.md)，明确其运行与保存能力。

核查状态（2026-10-18）：已按[Copilot官方Agent Skills说明](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)及[自定义指令说明](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)静态核对；本次未在VS Code/JetBrains等客户端实测，支持范围及实际调用须按所用产品与版本核验。
