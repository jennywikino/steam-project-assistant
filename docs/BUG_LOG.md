# Bug Log

## 1. 首页曾被误改成作品集说明页

- 结果：已回退。
- 规则：不要大改首页，首页 Feed 是核心。

## 2. 启动 bat 路径写死

- 结果：已修。
- 规则：bat 不能写死 `F:\ai` 等本机路径。

## 3. 安装采集环境 bat 中文乱码 / 无反馈

- 结果：已修到可用状态。
- 规则：bat 内容尽量 ASCII-only，中文说明放在 txt 或 README。

## 4. Playwright Chromium 下载慢

- 结果：改为优先使用本机 Microsoft Edge，Chromium 只作为可选。

## 5. 查查页默认显示鸣潮

- 结果：已修。
- 规则：外部展示版输入框默认空，不预填具体商业项目。

## 6. 首页图文源刷新入口太深

- 结果：已把联网刷新按钮前置，但后续筛选统一刷新仍未完全解决。

## 7. 当前待修：刷新 Steam 图文源后，部分 Feed 筛选仍显示旧数据

### 现象

点击“刷新 Steam 图文源（联网）”后，顶部时间更新，“全部”Feed 能看到新图文源项目；但切到“有 Demo/可试玩”“无发行/自发行”“热门/评论多”“潜力观察”“竞品参考”等筛选，仍显示 2026-06-22 或旧来源项目。

### 判断

筛选项可能没有统一基于 canonical feed cards，而是分别读取旧 `candidate_pool`、Steam 搜索导入、旧 `st.session_state` 或旧缓存。

### 状态

未解决。

## 8. 当前待修：Cat Mail Co. 多发行商显示不完整

### 事实

Cat Mail Co. / AppID 4380490 的 Steam 英文页和日文页都显示：

- Developer: Maracas Studio
- Publisher: Maracas Studio, Gamersky Games

如果工具只显示 Maracas Studio，优先怀疑缓存旧、publisher 解析只取第一个、字段合并覆盖或 UI 展示只显示第一项。

### 状态

未解决。
