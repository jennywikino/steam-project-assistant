# 当前任务：V0.9.3-P0b 首页 Feed 刷新后筛选仍显示旧数据

## 当前现象

点击首页顶部“刷新 Steam 图文源（联网）”后：

- 顶部提示联网刷新成功；
- 页面读取时间和图文源刷新时间更新；
- “全部”筛选能看到较新的 Steam 图文源项目；
- 但切换到“有 Demo/可试玩”“无发行/自发行”“热门/评论多”“潜力观察”“竞品参考”等筛选后，仍显示 2026-06-22 或旧 Steam 搜索导入 / 候选池项目；
- 再点刷新仍无法让这些筛选切换到最新图文源数据。

## 初步判断

首页 Feed 的各筛选项没有统一基于同一份 canonical cards。

可能存在：

- “全部”读 Steam 图文源；
- “最新采集”读 `browser_collected` / search import；
- “热门/评论多”读 `candidate_pool`；
- 筛选结果保存在 `st.session_state`；
- 刷新后没有清理 filtered cards / visible cards / load-more 状态；
- 刷新后没有 `st.rerun()`；
- 缓存函数没有 clear。

## 修复原则

- 不要改首页布局。
- 不要改候选池数据结构。
- 不要改导入主流程。
- 先定位首页 Feed 构建、刷新、筛选函数。
- 所有筛选必须从同一份 canonical cards 派生。
- 点击联网刷新后必须重建 canonical cards，并清理首页展示相关 `session_state`。
- 不要删除 `candidate_pool.csv`。
- 不要删除 `steam_browser_collected.csv`。
- 不要提交 `data/cache`、`dist`、`dist_test`、`tools/runtime`。

## 下一轮 Codex 建议档位

中。
