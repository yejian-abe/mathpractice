[app]
# APK 基本信息与依赖
title = 数学练习
package.name = mathpractice
package.domain = com.mpt
# 入口文件：main_android.py（Flask 子线程 + 浏览器 Intent）
source.dir = .
source.main = main_android.py
source.include_exts = py,txt,json,css,js,html,png,jpg
# 排除桌面专用/无关文件
source.exclude_dirs = data,build,dist,tests,__pycache__,.git,android_src
source.exclude_patterns = main.py,任务记录.md,*.spec,安装说明.txt,*.exe,*.zip

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
android.api = 31
android.minapi = 24
android.archs = arm64-v8a,armeabi-v7a
android.permissions = INTERNET
android.allow_backup = True
# CI 无交互终端，自动接受 Android SDK/NDK 许可协议（否则 build-tools 装不上导致 aidl 缺失）
android.accept_sdk_license = yes

[buildozer]
log_level = 2
warn_on_root = 1
