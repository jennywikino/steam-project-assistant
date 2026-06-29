# Project State

## 当前分支

`main`

## 当前最近可用 commit

`2e8f46b docs: add project handoff and agent guidance`

上一业务代码基线：`a7e45b8 fix: prefer Edge for Steam page collection`

## 当前版本状态

- V0.9.3-P0g 已修复 Early Access 已上线项目被旧 Coming Soon 状态误判为未上线/TBA。
- V0.9.3-P0f 已收口首页 Feed 信息架构：删除重复快捷入口、移动刷新入口、统一卡片来源/观察时间并明确非 Steam 全量库。
- V0.9.3-P0e 已为首页 Feed 增加观察窗口和时间口径，所有筛选先经过日期范围过滤。
- V0.9.3-P0d 将首页 Feed 收口为五个可解释筛选并禁止隐式旧来源补位；P0e 已用显式观察窗口替代“仅最新批次”限制。
- V0.9.3-P0c 已将最新 Steam 图文源前 30 个 AppID 接入轻量基础信息/评论补全，并在筛选前合并缓存字段。
- V0.9.3-P0b 已统一首页 canonical Feed 的筛选派生与刷新后展示状态失效逻辑。
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

- 首页 Feed 补全、筛选、观察窗口和信息架构已完成代码及本地缓存验证；建议在真实浏览器完成一次紧凑布局和五筛选 UI 回归。
- release_status 可能保留旧 Coming Soon 文本；首页未上线判断会优先采用发布日期、评论、在线和可购买证据，但源缓存仍建议定期刷新。
- TBA、发行商、开发商、发售日期和评论数目前只有当前值；追踪字段何时变化仍需要历史快照功能。
- 评论补全依赖 Steam appreviews；无评论项目会得到已确认的 0，网络失败项目保持待补状态。
- publisher 多发行商字段可能只显示第一项或被旧缓存覆盖。
- 打包脚本仍有历史残留，不作为当前主线任务。
- `dist/`、`dist_test/`、`tools/runtime/` 是本地残留，不应提交。
