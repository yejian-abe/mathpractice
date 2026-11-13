# -*- coding: utf-8 -*-
"""题量配置读写（data/config.json）"""
import json
import os

# 默认配置：每日 5 计算 + 4 竖式/解方程 + 2 应用题
DEFAULT_CONFIG = {
    "calc_count": 5,
    "vertical_count": 4,
    "word_count": 2,
}


def _config_path(data_dir):
    return os.path.join(data_dir, "config.json")


def load_config(data_dir):
    """读取配置，文件不存在或损坏时返回默认配置"""
    path = _config_path(data_dir)
    merged = dict(DEFAULT_CONFIG)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                saved = json.load(f)
            if isinstance(saved, dict):
                merged.update(saved)
        except (ValueError, OSError):
            pass
    return merged


def save_config(data_dir, cfg):
    """保存配置到 JSON 文件"""
    os.makedirs(data_dir, exist_ok=True)
    with open(_config_path(data_dir), "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
