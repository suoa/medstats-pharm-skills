#!/usr/bin/env python3
"""仅生成教学模拟数据，不计算答案；默认写到独立目录，避免覆盖教学输入。"""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 20261017


def generate_datasets(output_dir, *, seed=SEED, overwrite=False):
    """同版本依赖和种子产生同样的数据值；新增数据时勿改已有随机抽取顺序。"""
    output_dir = Path(output_dir)
    filenames = ("bioeq_cmax.csv", "tablet_assay.csv", "adverse_events.csv")
    if not overwrite and any((output_dir / name).exists() for name in filenames):
        raise FileExistsError("目标已有数据；另选目录，或明确使用 --overwrite。")
    rng = np.random.default_rng(seed)

    # 对数尺度配对数据，只演示等效界值；无序列、周期或完整PK参数。
    n = 24
    subject_effect = rng.normal(0, 0.35, n)
    log_r = np.log(500.0) + subject_effect + rng.normal(0, 0.15, n)
    log_t = np.log(500.0) + subject_effect + np.log(1.02) + rng.normal(0, 0.15, n)
    paired = pd.DataFrame({
        "subject_id": [f"S{i:02d}" for i in range(1, n + 1)],
        "cmax_R": np.round(np.exp(log_r), 1),
        "cmax_T": np.round(np.exp(log_t), 1),
    })

    # 每片为独立观测的教学假设，不据此推广真实批次或工艺效果。
    assay_a = rng.normal(98.5, 1.2, 20)
    assay_b = rng.normal(99.5, 1.0, 20)
    tablet = pd.DataFrame({
        "tablet_id": [f"{group}{i:02d}" for group in ("A", "B") for i in range(1, 21)],
        "process": ["A_对照工艺"] * 20 + ["B_新工艺"] * 20,
        "assay_pct": np.round(np.r_[assay_a, assay_b], 2),
    })

    a_flag = np.r_[np.ones(24, dtype=int), np.zeros(96, dtype=int)]
    b_flag = np.r_[np.ones(8, dtype=int), np.zeros(112, dtype=int)]
    rng.shuffle(a_flag)
    rng.shuffle(b_flag)
    adverse = pd.DataFrame({
        "subject_id": [f"P{group}{i:03d}" for group in ("A", "B") for i in range(1, 121)],
        "drug": ["A药"] * 120 + ["B药"] * 120,
        "adverse_event": np.r_[a_flag, b_flag],
    })
    output_dir.mkdir(parents=True, exist_ok=True)
    frames = dict(zip(filenames, (paired, tablet, adverse)))
    for filename, frame in frames.items():
        frame.to_csv(output_dir / filename, index=False, encoding="utf-8-sig")
    return frames


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("output/teaching-generated"))
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    generate_datasets(args.output_dir, seed=args.seed, overwrite=args.overwrite)
    print(f"已生成三份教学模拟CSV：{args.output_dir}（seed={args.seed}）；未计算参考答案。")


if __name__ == "__main__":
    main()
