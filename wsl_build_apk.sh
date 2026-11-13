#!/bin/bash
# mathPractice_tool APK 构建脚本（在 WSL Ubuntu / 任意 Debian 系 Linux 中运行）
# 用法：WSL 中进入项目目录后执行  bash wsl_build_apk.sh
set -e

# 1. 系统依赖（首次构建需要）
echo "== 安装系统依赖 =="
sudo apt-get update -y
sudo apt-get install -y git zip unzip openjdk-17-jdk python3-pip \
    autoconf automake libtool pkg-config cmake build-essential ccache \
    libssl-dev libffi-dev

# 2. Python 依赖与 Buildozer
echo "== 安装 Buildozer =="
pip3 install --user --upgrade pip wheel
pip3 install --user --upgrade cython==0.29.36 buildozer virtualenv

export PATH="$PATH:$HOME/.local/bin"

# 3. 打包（首次会自动下载 Android SDK/NDK，约数 GB，耗时 30-60 分钟）
echo "== 开始构建 APK（首次构建耗时长，请耐心等待）=="
buildozer -v android debug

echo "== 构建完成 =="
ls -lh bin/*.apk
