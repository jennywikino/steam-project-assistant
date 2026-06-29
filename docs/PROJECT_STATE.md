# Project State

## 当前分支

`main`

## 当前最近可用 commit

`a7e45b8 fix: prefer Edge for Steam page collection`

## 当前版本状态

- v0.9.2 免安装 Python Edge 优先测试版已能启动。
- Steam 页面采集优先使用本机 Microsoft Edge。
- Playwright Chromium 改为可选，不再默认强制下载。
- 查查页默认鸣潮已清空。
- 根目录启动入口已收口。
- 免安装包不要提交进 Git，只作为 GitHub Release asset。

## 稳定功能

- 首页项目发现 Feed
- 查查 / Steam 项目直查
- 项目导入
- Steam 页面采集
- Steam 搜索导入
- SteamDB 粘贴导入
- 候选池
- 一键项目画像
- 导出

## 已知风险

- 首页 Feed 筛选项刷新后仍可能读取旧来源。
- Steam 图文源联网刷新与各筛选项数据源尚未完全统一。
- publisher 多发行商字段可能只显示第一项或被旧缓存覆盖。
- 打包脚本仍有历史残留，不作为当前主线任务。
- `dist/`、`dist_test/`、`tools/runtime/` 是本地残留，不应提交。
