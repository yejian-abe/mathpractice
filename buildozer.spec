[app]
# APK 基本信息与依赖
title = 数学练习
package.name = mathpractice
package.domain = com.mpt
# 入口文件：main_android.py（Flask 子线程 + 浏览器 Intent）。
# 注意：buildozer 1.6.0 不支持 source.main 重命名（run #17 教训），由
# CI 在构建前 cp main_android.py main.py 覆盖桌面入口来提供 Android 入口
source.dir = .
source.include_exts = py,txt,json,css,js,html,png,jpg,svg
# 排除桌面专用/无关文件（main.py 不能排除：CI 已将其替换为 Android 入口）
# data 目录必须打包（否则 APK 无应用题题库，实时生成的模板名又与单元表
# 名不一致会被单元过滤拒绝，1-2 年级更无实时模板 → 应用题恒为 0）；
# 仅排除运行时数据：题集/配置/用户/抽题进度/压轴题推送进度/真题卷答卷，
# 不预置进 APK（压轴题配图 SVG 已由 include_exts 打包）
source.exclude_dirs = build,dist,tests,__pycache__,.git,android_src
source.exclude_patterns = 任务记录.md,*.spec,安装说明.txt,*.exe,*.zip,\
    data/daily/*,data/config.json,data/users.json,data/bank/progress_*,\
    data/finale/*,data/papers/*

version = 1.0

# 应用图标（512x512 PNG，安装后在桌面显示）
icon.filename = icon.png

# 依赖：仅保留 APK 运行必需项。reportlab/pillow/lxml/python-docx 用于桌面端
# PDF/Word 导出——p4a 的 reportlab recipe 下载源 hg.reportlab.com 已失效（403），
# 且这些库仅服务端导出用，安卓端停用导出（routes 做运行时检测返回友好提示）
requirements = python3,kivy,pyjnius,flask

# 启动不显示 Kivy 窗口内容（窗口会被浏览器覆盖）
fullscreen = False
orientation = all

# Android 配置
# targetSdk 31 触发 release 构建 Lint fatal（ExpiredTargetSdkVersion，要求 ≥33），
# 提到 34：runner 预装 SDK 已有 android-34 平台，且为 2024-25 年 Google Play 要求线
android.api = 34
android.minapi = 24
android.archs = arm64-v8a,armeabi-v7a
android.permissions = INTERNET
android.allow_backup = True
# CI 无交互终端，自动接受 Android SDK/NDK 许可协议（否则 build-tools 装不上导致 aidl 缺失）
android.accept_sdk_license = yes

[buildozer]
log_level = 2
warn_on_root = 1
