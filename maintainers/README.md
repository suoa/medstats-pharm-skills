# maintainers/（维护者工作区）

本目录是仓库维护者使用的工程工具与验收记录，**学生不需要安装或阅读**。学生只需用 `skills/` 里的技能、`datasets/teaching/` 里的数据和 `templates/student-project/` 模板。

## 目录

| 路径 | 用途 |
|---|---|
| `scripts/analyze_teaching.py` | 三份教学数据的完整分析（输出 results.json/summary.csv/summary.txt/列联表/Q–Q 图），用于冻结参考答案与回归核对 |
| `scripts/build_spss_check.py` | 生成 SPSS 机房验收便携包（语法 + 数据副本 + Python 复算参考值 + 空白实测记录 + SHA-256 清单）；不运行 SPSS |
| `scripts/validate_teaching.R` | 基础 R/stats 独立复核 Python summary 的数值字段 |
| `data_generation/generate_datasets.py` | 固定种子 20261017 重新生成三份 CSV（与仓内版本逐字节一致）；不计算参考答案 |
| `tests/` | 28 项 Python 测试（unittest）+ R 模板代码块执行测试 |
| `spss_pack/` | 四份 SPSS 语法源文件（打包器输入） |
| `qa/` | 评审、router 盲测、SPSS 与课堂试用的验收记录（含未执行项的如实标注） |
| `CHANGELOG.md` | 版本变更记录 |
| `requirements-teaching.txt` | 分析脚本依赖版本（学生按技能文档装 pandas/scipy/statsmodels 即可，不必装此锁定清单） |

## 常用命令（仓库根目录执行）

```bash
# Python 测试（28 项）
python -m unittest discover -s maintainers/tests -t . -v

# 完整教学分析（输出目录必须不存在）
python maintainers/scripts/analyze_teaching.py --output-dir /tmp/teaching-out --t-policy course

# 数据复现
python maintainers/data_generation/generate_datasets.py --output-dir /tmp/teaching-generated

# R 复核（需本机安装 R；当前云环境无 Rscript，未在此环境运行）
Rscript maintainers/tests/test_R_templates.R

# SPSS 便携包（生成后仍须在装有 SPSS Statistics 的机房实跑）
python maintainers/scripts/build_spss_check.py --output-dir /tmp/spss-check
```

## 已验证 / 未验证边界（v0.1.1）

- 已在当前云环境（Python 3.13、scipy/pandas/statsmodels）实跑：28 项 Python 测试全过；三份 CSV 可由种子逐字节复现；分析脚本数字与技能例题一致。
- 未在本环境运行：桌面 R（无 Rscript）、SPSS（无 Statistics）。`qa/validation.md` 中 R 4.6.0/WebR 的 99 字段复核为外部评审方提供的记录；SPSS 状态一律 `not_executed`，机房实机验证前不得对外宣称三轨均已通过。
