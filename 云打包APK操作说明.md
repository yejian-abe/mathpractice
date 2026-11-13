# 云打包 APK 操作说明（GitHub Actions 方案）

> 2026-11-12 记录。WSL 本机构建方案已取消，改用 GitHub 云端打包，本机无需安装 WSL/Java/Android SDK。

## 一、方案原理

把项目代码上传到 GitHub 仓库，由 GitHub 免费云端 Ubuntu 服务器自动构建 APK：

1. GitHub 检测到仓库中的 `.github/workflows/build_apk.yml`
2. 云端机器自动安装 JDK 17、Buildozer、系统编译依赖
3. 执行 `buildozer android debug` 编译出 APK
4. APK 作为构建产物（Artifact）挂在构建结果页，网页下载即可

构建配置文件：`.github/workflows/build_apk.yml`（已备好，手动触发模式 workflow_dispatch）

## 二、前置条件

| 条件 | 说明 |
|------|------|
| GitHub 账号 | 在 github.com 免费注册 |
| git | 本机已装 2.41，无需再装 |
| 仓库类型 | 建议 Public（公开），构建时长完全免费；私有仓库每月 2000 分钟免费额度 |
| 网络 | 上传代码和下载产物需要能访问 github.com |

## 三、操作步骤

### 第 1 步：创建 GitHub 仓库

1. 登录 github.com → 右上角 "+" → New repository
2. 仓库名随意（如 `mathpractice`）
3. 选择 **Public**
4. 不要勾选任何初始化选项（README / .gitignore / license 都不勾）
5. 点 Create repository，记下仓库地址（如 `https://github.com/你的用户名/mathpractice.git`）

### 第 2 步：上传代码

两种方式任选：

**方式 A：命令行 git 推送（由助手代做，需授权）**

助手会先准备好 `.gitignore`（排除 `dist/`、`build/`、`data/daily/`、`data/users.json`、`data/config.json` 等大文件和用户数据；GitHub 单文件上限 100MB），然后执行：

```bash
cd mathPractice_tool
git init
git add .
git commit -m "init"
git branch -M main
git remote add origin https://github.com/你的用户名/mathpractice.git
git push -u origin main
```

首次推送会弹出浏览器要求登录 GitHub 授权（或使用个人访问令牌 Personal Access Token 作为密码）。

**方式 B：网页手动上传**

1. 打开新建的空仓库页面 → "uploading an existing file" 链接
2. 把项目文件夹内容拖入（注意不要拖入 `dist/`、`build/`、`data/daily/`、`__pycache__/`）
3. 点 Commit changes 提交

### 第 3 步：触发云端构建

1. 打开仓库页面 → 顶部 **Actions** 标签
2. 左侧列表选 "Build Android APK"
3. 右侧点 **Run workflow** → 绿色按钮确认运行

### 第 4 步：等待构建并下载 APK

1. 构建耗时约 **30~60 分钟**（首次较慢，页面可实时查看日志）
2. 构建完成后（绿色对勾）进入该次构建详情页
3. 页面底部 **Artifacts** 区域下载 `mathpractice-apk`（是一个 zip 包）
4. 解压得到 APK 文件

### 第 5 步：安装到安卓平板

1. 把 APK 拷贝到安卓平板（数据线 / 微信 / 网盘均可）
2. 平板上点击 APK 文件安装（首次需允许"安装未知来源应用"）
3. 点击桌面"数学练习"图标启动：应用内部启动 Flask 服务并自动调起系统浏览器打开 `http://127.0.0.1:10021`
4. 若浏览器未自动打开，手动打开浏览器访问 `http://127.0.0.1:10021`

## 四、打包前必须修正的问题（已列入待办）

`buildozer.spec` 目前排除了整个 `data` 目录，而题库 JSON 在 `data/bank/` 下，直接打包会导致 APK 内**没有题库**。修正规则：

- 包含：`data/bank/`（12 份分册题库，运行必需）
- 排除：`data/daily/`、`data/users.json`、`data/config.json`（用户运行数据，不应预置进 APK）

## 五、已知风险与应对

| 风险 | 应对 |
|------|------|
| lxml / python-docx 在 p4a 打包失败 | 从 requirements 去掉这两项，安卓版停用 Word 导出（PDF 导出不受影响），改完重新 Run workflow |
| 首次构建 30-60 分钟无输出 | 正常现象，Actions 页面日志会持续滚动 |
| 构建日志报 cython 版本错误 | workflow 已固定 cython==0.29.36，一般不会遇到；若遇到把报错发给助手 |
| 后续改了代码要重新打包 | 本地提交并 `git push` 后，再到 Actions 页点一次 Run workflow 即可 |

## 六、方案对比备忘

| | WSL 本机方案（已取消） | GitHub 云打包（采用） |
|---|---|---|
| 本机改动 | 装 WSL + 重启电脑 | 无 |
| 单次耗时 | 30-60 分钟 | 30-60 分钟 |
| 费用 | 免费 | 公开仓库免费 |
| 重复打包 | 本机一键脚本 | 推送代码后网页点 Run |
