# 🍅 番茄钟桌面应用 Pomodoro Timer

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)
![Pillow](https://img.shields.io/badge/Pillow-10%2B-yellow?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-22C55E)
![Release](https://img.shields.io/github/v/release/BOEING2408/pomodoro-app?color=FF6B6B)
![Stars](https://img.shields.io/github/stars/BOEING2408/pomodoro-app?style=social)

**一款精美的番茄钟桌面应用，帮助你专注工作、高效完成任务。**

[📥 立即下载](#-快速开始) · [✨ 功能特性](#-功能特性) · [🚀 快速开始](#-快速开始) · [📖 使用说明](#-使用说明)

</div>

---

## ✨ 功能特性

### ⏱ 智能计时器
- 三种模式：**专注 25 分钟 / 短休息 5 分钟 / 长休息 15 分钟**
- 圆环进度动画实时显示剩余时间
- 每完成 4 个番茄自动切换长休息
- 完成后系统提示音 + 弹窗通知

### 📋 任务列表
- 添加、完成、删除任务
- 点击任务名称设为当前任务，番茄完成后自动累计
- 已完成任务显示删除线样式

### 📊 每日进度汇总
- 完成番茄数 / 专注时长 / 完成任务数 / 待办任务数
- 任务完成率进度条
- 近 7 日番茄柱状图（今日高亮）

### 🎯 专注模式
- 全屏置顶覆盖层，排除一切干扰
- 超大圆环倒计时 + 当前任务显示
- 每 500ms 强制置顶，防止其他窗口遮挡
- Esc 键或按钮退出（需二次确认）

### 🖼 自定义背景图片
- 支持 JPG / PNG / BMP / WebP / TIFF / GIF
- 模糊（0~20）+ 压暗（10%~90%）参数调节
- 专注模式中可直接更换背景
- 设置自动持久化

### 💬 励志语录
- 内置 **39 条**中英双语励志语录（专注、坚持、时间、成长、自律等主题）
- 专注模式下定时轮换，带**淡入淡出动画**
- 支持自定义添加/删除语录
- 轮换间隔可调（10~300 秒）
- 一键开关语录功能

---

## 🚀 快速开始

### 方式一：下载 Release（推荐）

前往 [Releases 页面](https://github.com/BOEING2408/pomodoro-app/releases) 下载最新版本的 `pomodoro-app-v1.0.0.zip`，解压后双击 `start.bat` 即可运行。

> **前提条件：** 已安装 [Python 3.10+](https://www.python.org/downloads/)（安装时勾选「Add Python to PATH」）并执行 `pip install Pillow`

### 方式二：克隆源码

```bash
# 克隆仓库
git clone https://github.com/BOEING2408/pomodoro-app.git
cd pomodoro-app

# 安装依赖
pip install Pillow

# 启动应用
python pomodoro.py
```

### 依赖说明

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | 3.10+ | 运行环境（含 tkinter） |
| Pillow | 10+ | 背景图片处理 |

> tkinter 是 Python 标准库的一部分，使用官方安装包默认已包含，无需单独安装。

---

## 📖 使用说明

### 基本操作

| 操作 | 说明 |
|------|------|
| **▶ 开始 / ⏸ 暂停** | 启动或暂停当前计时器 |
| **↺ 重置** | 重置当前模式计时器 |
| 点击模式按钮 | 切换专注 / 短休息 / 长休息 |
| 点击任务名 | 设为当前任务（高亮显示） |
| 点击 ⬜ | 标记任务完成/未完成 |
| 点击 ✕ | 删除任务 |

### 专注模式

1. 点击「**🎯 进入专注模式**」按钮（计时器会自动开始）
2. 全屏覆盖层展开，显示超大倒计时圆环
3. 底部励志语录每隔设定时间自动切换
4. 按 **`Esc`** 或点击「⏹ 退出专注」退出

### 自定义背景图片

1. 在左侧面板「🖼 专注背景图片」区域点击「📂 选择图片」
2. 调节**模糊**和**压暗**滑块至满意效果
3. 进入专注模式即可看到自定义背景

### 励志语录管理

1. 在左侧面板「💬 励志语录」区域可开关语录功能
2. 调节**轮换间隔**（默认 60 秒）
3. 点击「＋ 添加语录」输入自定义语录和作者
4. 在专注模式中点击「⏭ 下一条语录」手动切换

---

## 📁 项目结构

```
pomodoro-app/
├── pomodoro.py          # 主程序
├── start.bat            # Windows 一键启动脚本
├── README.md            # 说明文档
├── .gitignore           # Git 忽略规则
└── pomodoro_data.json   # 用户数据（运行后自动生成，不纳入版本控制）
```

---

## 🎨 界面布局

| 区域 | 说明 |
|------|------|
| 左侧面板 | 计时器圆环、模式切换、控制按钮、背景/语录设置 |
| 右上区域 | 任务列表（可滚动） |
| 右下区域 | 今日进度汇总 + 近 7 日柱状图 |
| 专注模式 | 全屏深色/自定义背景 + 超大倒计时 + 励志语录 |

---

## 📦 数据说明

用户数据自动保存在程序同目录下的 `pomodoro_data.json`，包含：
- 任务列表及完成状态、番茄计数
- 每日番茄记录（用于进度汇总和历史图表）
- 应用设置（背景图路径、语录开关、轮换间隔等）
- 自定义语录库

该文件已加入 `.gitignore`，不会上传到版本控制，数据完全本地保存。

---

## 🗺 开发路线图

- [x] 番茄计时器（专注/短休/长休）
- [x] 任务列表管理
- [x] 每日进度汇总 + 近 7 日图表
- [x] 全屏专注模式（置顶守护）
- [x] 自定义背景图片（模糊/压暗）
- [x] 励志语录（淡入淡出 + 自定义）
- [ ] 统计数据导出（CSV/Excel）
- [ ] 多主题皮肤切换
- [ ] 自定义番茄时长
- [ ] 桌面通知（系统托盘）

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建功能分支：`git checkout -b feature/your-feature`
3. 提交更改：`git commit -m 'feat: 添加某功能'`
4. 推送分支：`git push origin feature/your-feature`
5. 提交 Pull Request

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源，自由使用、修改和分发。

---

<div align="center">

Made with ❤️ and 🍅

如果这个项目对你有帮助，欢迎点个 ⭐ Star！

</div>
