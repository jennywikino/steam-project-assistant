# Steam Project Assistant

Steam 独立游戏项目初筛助手｜面向独立游戏发行选品场景的本地工作台

将 Steam 项目发现、资料补全、候选池筛选、单项目画像和报告导出整理为一个可复用工作流，用于辅助发行/运营人员更快判断项目是否值得试玩、观察或联系。

![首页项目发现 Feed](docs/portfolio/01_home_feed.png)

## 项目定位

面向独立游戏发行选品场景的本地工作台，用于整理项目线索、补全公开信息并沉淀初筛结果。

## 解决的问题

独立游戏发行找项目时，信息分散在 Steam 搜索、SteamDB、商店页、评论、公告和人工表格中。本工具用于把这些零散信息整理成候选池，并辅助判断项目是否值得试玩、观察或联系。

## 核心工作流

项目发现 Feed → 项目导入 → 候选池管理 → 基础资料补全 → 一键项目画像 → 报告导出

## 功能展示

### 项目导入

![项目导入](docs/portfolio/03_import.png)

### 候选池工作台

![候选池工作台](docs/portfolio/05_candidate_pool.png)

### 一键项目画像

![一键项目画像](docs/portfolio/04_project_profile.png)

## 核心功能

| 模块 | 作用 |
|---|---|
| 首页项目发现 Feed | 展示最近采集项目、候选池概览和项目卡片 |
| 项目导入 | 支持 Steam 搜索结果、Steam 页面采集、SteamDB 文本 / 链接 / AppID 导入 |
| 候选池管理 | 支持状态筛选、优先级标记、下一步动作和备注 |
| 基础信息补全 | 补全开发商、发行商、发售状态、Demo、简中、类型、评论等字段 |
| 本地规则建议 | 根据资料完整度、发售状态、Demo、评论等字段给出初筛建议 |
| 一键项目画像 | 生成单项目基础信息、评论样本、公告记录和导出报告 |
| 导出 | 支持 CSV / Excel / TXT 输出 |

## 技术实现

- 前端与交互：Streamlit
- 数据处理：Python / Pandas
- 页面采集：Playwright
- 数据源：Steam 商店页 / Steam appdetails / SteamDB 粘贴文本
- 本地存储：CSV / JSON cache
- 导出格式：CSV / Excel / TXT

## 当前限制

- 当前定位是本地发行工作台，不是完整 SaaS
- 部分 Steam 字段依赖页面结构和网络状态，可能需要手动校验
- SteamDB 当前只做粘贴解析，不自动爬取
- 本地规则建议不是 AI 判断，仅用于初筛辅助
- 展示截图和样例数据会进行脱敏处理

## 后续方向

- Demo 数据模式
- 在线演示版本
- AI 辅助项目画像
- 展会数据源接入
- 更稳定的打包版本

## 简历描述参考

使用 Python、Streamlit、Pandas 与 Playwright 搭建独立游戏发行选品工作台，将 Steam 项目发现、资料补全、候选池筛选、单项目画像和报告导出整理为可复用的本地工作流。

Copyright © 2026 Jennifer. All rights reserved.

This repository is published for portfolio review and technical demonstration only.
No permission is granted for commercial use, redistribution, or derivative works without explicit written consent.
