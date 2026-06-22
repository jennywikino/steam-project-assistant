# Steam Project Assistant

Steam 独立游戏项目初筛助手

## 项目定位

面向独立游戏发行选品场景的内部效率工具。

## 解决的问题

独立游戏发行找项目时，信息分散在 Steam 搜索、SteamDB、商店页、评论、公告和人工表格中。本工具用于把这些零散信息整理成候选池，并辅助判断项目是否值得试玩、观察或联系。

## 核心工作流

项目发现 Feed → 项目导入 → 候选池管理 → 基础资料补全 → 一键项目画像 → 报告导出

## 功能展示截图占位

截图将在完成脱敏和统一尺寸后补充，命名与展示顺序如下：

1. 首页项目发现 Feed：`docs/portfolio/01_home_feed.png`
2. 项目导入：`docs/portfolio/02_import.png`
3. 候选池工作台：`docs/portfolio/03_candidate_pool.png`
4. 基础资料补全队列：`docs/portfolio/04_enrich_queue.png`
5. 一键项目画像：`docs/portfolio/05_project_profile.png`
6. 导出结果：`docs/portfolio/06_export.png`

截图要求和说明见 [`docs/portfolio/README.md`](docs/portfolio/README.md)。

## 核心功能

- 首页项目发现 Feed
- Steam 搜索结果导入
- Steam 页面采集
- SteamDB 文本 / 链接 / AppID 解析
- 候选池筛选和批量处理
- Steam 基础信息补全
- 本地规则建议
- 一键项目画像
- CSV / Excel / TXT 导出

## 技术栈

Python / Streamlit / Pandas / Playwright / CSV 本地数据流 / Steam 页面数据解析

## 当前限制

- 不是完整 SaaS
- 部分 Steam 数据依赖网络和页面结构
- 本地建议不是 AI 判断
- SteamDB 当前为粘贴解析，不做自动爬取

## 后续方向

- Demo 数据模式
- 在线演示版本
- AI 辅助项目画像
- 展会数据源接入
- 更稳定的打包版本

## 简历描述参考

使用 Python、Streamlit、Pandas 与 Playwright 搭建独立游戏发行选品工作台，将 Steam 项目发现、资料补全、候选池筛选、单项目画像和报告导出整理为可复用的本地工作流。
