# -*- coding: utf-8 -*-
"""用户管理：本地多用户（无密码，家庭工具）
存储：data/users.json → {"users": [{"id","name","created_at"}], "next_seq": N}
默认用户 id="default"，老题集文件（文件名无用户后缀）自动归属默认用户。
"""
import json
import os
from datetime import datetime

from app.services import bank


def _path(data_dir):
    return os.path.join(data_dir, "users.json")


def _load_raw(data_dir):
    path = _path(data_dir)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (ValueError, OSError):
        return None


def save_users(data_dir, data):
    """保存用户数据（data_dir 目录已存在）"""
    with open(_path(data_dir), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_users(data_dir):
    """读取用户列表；首次访问（或数据损坏）时自动创建默认用户"""
    data = _load_raw(data_dir)
    if (not isinstance(data, dict)
            or not isinstance(data.get("users"), list)
            or not data["users"]):
        data = {
            "users": [{"id": "default", "name": "默认用户",
                       "created_at": datetime.now().isoformat()}],
            "next_seq": 1,
        }
        save_users(data_dir, data)
    return data


def list_users(data_dir):
    return load_users(data_dir)["users"]


def create_user(data_dir, name):
    """创建用户，返回 (user, error)；重名时返回 (None, 错误信息)"""
    name = (name or "").strip()
    if not name:
        return None, "姓名不能为空"
    data = load_users(data_dir)
    if any(u.get("name") == name for u in data["users"]):
        return None, "该姓名已存在"
    uid = "u%d" % data["next_seq"]
    data["next_seq"] = data["next_seq"] + 1
    user = {"id": uid, "name": name, "created_at": datetime.now().isoformat()}
    data["users"].append(user)
    save_users(data_dir, data)
    return user, ""


def delete_user(data_dir, user_id):
    """删除用户并连带删除其全部题集（默认用户不可删除）"""
    if user_id == "default":
        return False, "默认用户不可删除"
    data = load_users(data_dir)
    if not any(u.get("id") == user_id for u in data["users"]):
        return False, "用户不存在"
    data["users"] = [u for u in data["users"] if u.get("id") != user_id]
    save_users(data_dir, data)
    _remove_user_sets(data_dir, user_id)
    bank.remove_progress(data_dir, user_id)  # 连带清理题库抽题进度
    return True, ""


def _remove_user_sets(data_dir, user_id):
    """删除该用户的全部题集文件（文件名后缀 _u{user_id}.json）"""
    d = os.path.join(data_dir, "daily")
    if not os.path.isdir(d):
        return
    suffix = "_u%s.json" % user_id
    for fn in os.listdir(d):
        if fn.endswith(suffix):
            try:
                os.remove(os.path.join(d, fn))
            except OSError:
                pass
