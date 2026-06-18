# PROJECT_STATUS

## 当前项目状态

- 项目名称：Steam 项目初筛助手
- 当前版本：V0.8.4 项目导入页操作闭环与入池反馈
- 当前定位：面向独立游戏发行/运营场景的本地 Steam 项目筛选工作台

## 当前已完成 V0.8.4

- 项目导入页增加选择状态说明，明确已选项目会发送到竞品与候选 / 候选池。
- Steam 搜索导入、Steam 页面采集、SteamDB 粘贴导入表格上下增加“发送到候选池 / 查看已选项目 / 清空当前选择”动作栏。
- 新增已选项目预览，默认最多展示 30 条。
- 新增当前项目标准信息快照，提供打开 Steam、查查、项目画像、加入候选池入口。
- 发送候选池后显示本次发送结果面板，包含新增、补空字段、已存在未变更、失败和明细。
- 发送结果支持跳转候选池，并携带来源、批次和本次 AppID 列表。
- 普通模式隐藏完整导入表 / 调试数据。
- 保持 V0.8 功能冻结，不新增抓取能力，不改现有导入请求逻辑。

## 当前已完成 V0.8.3

- 顶部导航合并三个导入入口为“项目导入”。
- 项目导入页内部提供 Steam 搜索导入、Steam 页面采集、SteamDB 粘贴导入三种模式。
- 默认进入 Steam 搜索导入，保留原保守导入数量和请求逻辑。
- Steam 页面采集和 SteamDB 粘贴导入保留原功能，仅移动入口与统一命名。
- 旧跳转目标兼容到“项目导入”并自动选择对应导入模式。
- 不新增抓取能力，不改现有导入、候选池和导出逻辑。

## 当前已完成 V0.8.1

- 首页从作品集说明页收口为今日发行筛选工作台。
- 首页首屏改为薄头部，不再展示大块关键能力宣传卡片。
- 首页保留当前项目状态、快捷入口、项目发现 Feed、动作反馈和最近操作记录。
- 首页主视觉只保留“刷新首页”作为刷新入口；高级刷新和缓存维护默认折叠。
- 旧版雷达、常用工具、手动观察、快照和调试 JSON 不再占首页主视觉。
- 项目卡片只保留打开 Steam、加入候选池、项目画像、忽略四个主动作。
- 加入候选池后显示已在候选池、加入时间、查看候选池和生成项目画像入口。
- 项目画像动作写入状态与最近操作记录，并提供打开项目画像页入口。
- 忽略动作写入候选池归档状态并进入最近操作记录，不物理删除项目数据。
- 新增轻量 `data/action_log.csv`，记录加入候选池、发送项目画像、忽略等首页动作。

## 当前已完成 V0.8.0-P1

- 修复 Steam 搜索批量导入清空后 selected 统计报错，不再出现 `int("")`。
- Steam 浏览器采集页和 Steam 搜索批量导入页使用 session_state AppID 集合维护选择状态。
- 全选当前筛选结果不再写 CSV，减少几百行表格时的卡顿。
- 两个导入页默认只展示前 100 条，完整表格进入调试折叠区。
- Steam 搜索批量导入支持清空确认、清空备份和按 AppID 去重备份。
- 清空采集/导入时同步清空页面选择状态，不影响 `candidate_pool.csv`。
- 侧边栏启动/停止说明默认折叠。
- 新增 `启动工具_无黑窗.vbs`，不改变原 bat 启动脚本。

## 当前已完成 V0.8.0

- 首页新增作品集 Hero 区域，首屏明确项目定位。
- 首页新增 4 个关键能力卡片：批量导入、项目补全、发行初筛、候选沉淀。
- 首页新增推荐工作流：导入项目、补全信息、筛选分流、沉淀导出。
- 主导航显示顺序整理为：首页、查查、Steam 浏览器采集、Steam 搜索批量导入、SteamDB 导入、竞品与候选、一键项目画像、历史与导出、文档与状态。
- README 已重写为展示版。
- 新增 `docs/USER_GUIDE.md` 和 `docs/PORTFOLIO_NOTE.md`。
- 补充项目定位、核心功能、使用流程、安全限制和作品集说明。
- V0.8 进入作品集展示阶段，不新增核心抓取功能。

## 当前边界

- 不接 AI。
- 不新增 Steam API。
- 不新增 SteamDB 自动抓取。
- 不新增 B站/YouTube。
- 不改候选池核心逻辑。
- 不改 Steam 搜索批量导入请求逻辑。
- 不改 Excel 导出逻辑。
- 不提交真实采集数据、缓存、公司项目数据。

## 当前项目状态

- 项目名称：Steam 项目初筛助手
- 当前版本：V0.7.4 高频入口与 Steam 批量导入收口版
- 当前定位：本地 Steam 项目发现、发行初筛与候选池工作台

## 当前已完成 V0.7.4 高频入口与 Steam 批量导入收口版

- 查查入口前置，主导航第 2 位统一显示为“查查”。
- 新增 Steam 搜索批量导入，支持 Coming Soon / Demo 池分页导入。
- Steam 搜索导入支持自定义 Steam 搜索 URL，并默认限制最大导入数量。
- Steam 浏览器采集表和 Steam 搜索导入表支持批量选择。
- Steam 链接列改为可点击的“打开 Steam”。
- 新品节 / 搜索页不再只依赖手动点“显示更多”。
- SteamDB 手动导入保留，SteamDB 自动抓取 / 新上架监控不在主导航。
- V0.8.0 后续进入作品集展示与文档收口。

## 当前已完成 V0.7.3.3 首页 Feed 真实筛选收口版

- 首页 Feed 分类改为真实发行筛选口径。
- 新增最新采集、未上线/TBA、有 Demo/可试玩、无发行/自发行、热门/评论多、潜力观察、竞品参考。
- 每个分类支持独立加载更多。
- 首页卡片增加项目状态标签。
- 保留 Steam 浏览器采集为新项目发现主入口。
- V0.8.0 后续进入作品集展示与文档收口。

## 当前项目状态

- 项目名称：Steam 项目初筛助手
- 当前版本：V0.7.3.2 首页信息流与入口收口
- 当前定位：本地 Steam 项目发现、初筛与候选池工作台

## 当前已完成 V0.7.3.2 首页信息流与入口收口

- 下线 SteamDB 新上架监控入口，保留 SteamDB 手动粘贴导入。
- Steam 浏览器采集默认打开 Steam 商店首页。
- 首页改为项目发现 Feed，支持默认 12 个项目和加载更多。
- 首页低频工具收进“高级 / 低频工具”折叠区。
- 新项目发现主流程改为 Steam 浏览器采集 + SteamDB 手动粘贴导入。

## 当前项目状态

- 项目名称：Steam 项目初筛助手
- 当前版本：V0.7.3 Steam 浏览器采集助手 P0
- 当前定位：本地 Steam 项目初筛与交付输出工作台

## 当前已完成
V0.7.3 Steam 浏览器采集助手 P0：
- 新增 Steam 浏览器采集助手。
- 支持打开受控 Steam 浏览器。
- 支持从当前页面提取 Steam AppID。
- 支持补全基础信息。
- 支持发送到候选池。
- SteamDB Recent Events 因 403 不再作为主入口。
- Coming Soon / TBA 专项池后续再做。

V0.7.1 正式候选清理与导出落地：
- 新增正式候选 Sheet。
- 新增工作用日报 Sheet。
- 测试 / 竞品 / 放弃 / 暂缓项目不会污染正式候选导出。
- 日期格式统一暂缓到后续小修。

V0.7.0 可用输出版：
- 新增候选池 Excel 多 Sheet 导出。
- 新增今日日报 Sheet。
- 工具从“查询 / 候选池”进入“可交付输出版”。
- 暂不做 API / 网站 / AI。

V0.6.21 SteamDB AppID 基础信息补全：
- 新增 SteamDB 导入页的 AppID 基础信息补全。
- 支持缓存 Steam 基础信息到 `data/cache/steam_appdetails_cache.json`。
- 发送候选池时优先使用补全后的基础字段。
- 补全失败不影响 AppID-only 入池流程。


V0.6.20 SteamDB 工作流桥接：
- 项目画像数据概览改为缩框摘要。
- 新增 SteamDB 导入页面。
- 支持粘贴 SteamDB 榜单 / 链接 / 多行 AppID 并解析。
- 支持解析结果预览、选择、导入候选池。
- 新增 SteamDB 榜单观察记录。
- 候选池完整字段支持 SteamDB rank / followers / peak / source。

V0.6.19-data 项目数据层补齐：
- 统一项目数据字段。
- 增加数据完整度与缺失项提示。
- 项目画像增加数据概览条。
- Steam 动态 / 公告结构化显示。
- Steam 评论预览结构化显示。
- Demo / Playtest 状态统一。
- 第三方市场数据手动区统一。
- 项目画像报告和候选日报补充数据状态字段。

V0.6.18 日常工作流收束：
- 新增今日工作流页面。
- 串联候选池、查查、项目画像、日报导出。
- 支持选择当前处理项目并快速更新阶段、优先级和下一步动作。
- 首页增加进入今日工作流入口。

V0.6.17-lite 候选池轻量修复：
- 优化候选池 AppID 占位记录显示，资料不足字段在表格中有明确兜底。
- 查查 / 项目画像成功获取后可手动回写候选池基础信息。
- 候选池保留轻量“补全当前筛选结果”，最多处理 10 条资料不足或 AppID 占位记录。
- 放弃复杂 data_quality 和大型清理面板，避免工具变重。

V0.6.16 批量补全与今日候选日报：
- 新增候选池批量补全，支持当前筛选、资料不足、新发现和手动选择范围。
- 新增候选自动建议与建议理由，基于 Demo、简中、发行商、评论数和字段完整度做规则初筛。
- 新增今日候选日报 Excel 导出，包含今日新增、待处理、待试玩、值得联系、放弃 / 暂缓和全部候选。
- 首页增加今日候选工作台摘要，可查看今日新增、待处理、待试玩、值得联系、高优先级和资料不足数量。
- 候选池操作支持应用建议与待试玩、待开发商调查、值得联系、暂缓、放弃快速流转。

V0.6.15-hotfix1 候选池验收修复：
- 修复候选池发送到项目画像时修改已实例化 widget key 导致的 StreamlitAPIException。
- 恢复今日新游雷达标题附近的刷新按钮。
- 候选池筛选项按记录数量自适应折叠。
- 批量导入候选时补全 Steam 基础详情。
- 收紧批量导入 AppID 解析规则。

V0.6.15 候选池工作流闭环：
- 新增 `data/candidate_pool.csv` 项目候选池，独立于 `data/projects.csv`。
- 项目画像、今日新游雷达、SteamDB 发现均可加入项目候选池。
- 支持 stage、priority、next_action、备注、放弃原因和归档管理。
- SteamDB 发现支持批量导入 AppID / Steam 链接 / SteamDB 链接。
- 竞品与候选页新增“项目候选池”区域，可筛选、发送到查查 / 项目画像、打开 Steam / SteamDB、更新状态并导出 Excel。
- 首页 / 今日看板新增候选池摘要，支持快捷查看待试玩、值得联系和导出候选清单。

V0.6.11 第三方市场数据记录卡：
- 项目画像页新增第三方市场数据区，支持 VGI / Gamalytic / SteamDB / SteamSpy / Steam官方手动录入。
- 支持保存 `data/market_data.csv`，展示市场数据摘要和多来源对比表。
- 画像 Markdown 报告新增“第三方市场数据”节，并标注第三方估算限制。
- 新增 `config/data_sources.example.json` 作为未来 API 配置模板。

V0.6.10a 多开发商 / 多发行商搜索修复：
- 开发商/发行商字段支持按 `/`、逗号、分号和顿号拆分为单个公司。
- 开发商本体调查区可分别选择调查对象，并为每个开发商/发行商生成独立 Steam 搜索。
- 公司档案新保存时按单个公司名和角色落盘。

V0.6.10 开发商本体调查窗口：
- 项目画像页新增开发商/发行商本体调查区，自动带入 AppID、游戏名、开发商和发行商。
- 支持保存 `data/company_dossier.csv` 公司档案，记录联系方式、作品、发行合作史、证据摘要和可信度。
- 画像 Markdown 报告新增“开发商本体调查”节，保留人工复核边界。

1. V0.1 项目基础卡
2. V0.2 Demo 试玩记录
3. V0.2.1 历史记录、中文字段、Excel 导出
4. V0.3 竞品对照表
5. V0.3.5 竞品候选发现器
6. V0.3.6 可用性修复
7. V0.3.7 表单减负
8. V0.31 搜索中心
9. V0.31a 搜索中心打开链接
10. V0.31b 搜索中心平台导航
11. V0.31c 搜索策略与合并展示
12. V0.31d 搜索中心降噪
13. V0.31e 启停体验修复
14. V0.4 一键项目画像草稿
15. V0.4.1 画像压缩与竞品候选抓取
16. V0.4.2 竞品搜索纠偏与标题线索
17. V0.4.3 画像字段语义修正
18. V0.5 SteamDB 发现工作台
19. V0.5.1 无窗口启动器与后台服务管理
20. V0.5.2 首页情报面板
21. V0.5.3 首页信息流化
22. V0.5.4 首页视觉卡片与跳转修复
23. V0.5.5 首页新项目发现与快照卡片
24. V0.5.6 首页 Steam 图文源
25. V0.5.7 Steam 图文卡信息补全与首页废话清理
26. V0.5.8 Steam 首页源分类纠偏与 appdetails 强制补全
27. V0.5.9 启动入口统一与旧 bat 归档
28. V0.6.0 Steam 日常雷达卡片重构
29. V0.6.1b 项目画像商店图文预览
30. V0.6.15 候选池工作流闭环
31. V0.6.16 批量补全与今日候选日报
32. V0.6.17-lite 候选池轻量修复
33. V0.6.18 日常工作流收束
34. V0.6.19-data 项目数据层补齐
35. V0.6.20 SteamDB 工作流桥接
36. V0.6.21 SteamDB AppID 基础信息补全

## V0.6.21 更新

- 新增 SteamDB 导入页的 AppID 基础信息补全。
- 支持缓存 Steam 基础信息到 `data/cache/steam_appdetails_cache.json`。
- 发送候选池时优先使用补全后的基础字段。
- 补全失败不影响 AppID-only 入池流程。

## V0.6.20 更新

- 项目画像数据概览改为缩框摘要。
- 新增 SteamDB 导入页面。
- 支持粘贴 SteamDB 榜单 / 链接 / 多行 AppID 并解析。
- 支持解析结果预览、选择、导入候选池。
- 新增 SteamDB 榜单观察记录。
- 候选池完整字段支持 SteamDB rank / followers / peak / source。

## V0.6.19-data 更新

- 统一项目数据字段。
- 增加数据完整度与缺失项提示。
- 项目画像增加数据概览条。
- Steam 动态 / 公告结构化显示。
- Steam 评论预览结构化显示。
- Demo / Playtest 状态统一。
- 第三方市场数据手动区统一。
- 项目画像报告和候选日报补充数据状态字段。

## V0.6.18 更新

- 新增今日工作流页面。
- 串联候选池、查查、项目画像、日报导出。
- 支持选择当前处理项目并快速更新阶段、优先级和下一步动作。
- 首页增加进入今日工作流入口。

## V0.6.17-lite 更新

- 优化候选池 AppID 占位记录显示。
- 查查 / 项目画像成功获取后可回写候选池基础信息。
- 候选池保留轻量补全当前筛选结果。
- 放弃复杂 data_quality 和大型清理面板，避免工具变重。

## V0.6.16 更新

- 新增候选池批量补全。
- 新增候选自动建议与建议理由。
- 新增今日候选日报 Excel 导出。
- 首页增加今日候选工作台摘要。
- 候选池操作支持应用建议与快速流转。

## V0.6.15 更新

- 新增候选池数据文件 `data/candidate_pool.csv`。
- 支持从项目画像、今日新游雷达、SteamDB 发现加入候选。
- 支持候选状态、优先级、下一步动作管理。
- 支持批量导入 AppID / Steam 链接。
- 支持导出候选池 Excel。

## V0.6.1b 更新

- 一键项目画像新增商店图文预览。
- 展示 header 图、截图、视频缩略图和短描述。
- 增加视觉初判提示，复用 Steam appdetails 数据。

## V0.6.0 更新

- 新增 Steam 评价摘要模块：`modules/steam_review_stats.py`
- 新增评价缓存：`data/cache/steam_review_stats_cache.json`，按 AppID 缓存 12 小时
- 首页 Steam 图文卡新增好评率、评测数、评测摘要、评测样本中位/平均游玩时间
- 首页新增好评率、评测数、游玩时间中位数、当前折扣和价格筛选
- 新增 Steam 数据统一 normalizer：`modules/steam_data_normalizer.py`
- 首页发送到项目画像时写入 developer、publisher、genres、release_date、price 和评价数据
- 一键项目画像页新增好评率、评测数、评测摘要、中位游玩时间、平均游玩时间
- 项目画像页清理泛标题大段分析，改为紧凑发行判断卡、查看数据来源、查看竞品候选、查看人工待确认项
- 首页新增常用工具小方块：SteamDB、Steam 折扣、Top Rated、Wishlist、Followers、Calendar、B站搜索、小黑盒搜索、项目画像、搜索中心
- Excel `首页Steam图文源` sheet 新增评价摘要与评测样本游玩时间字段

## V0.3.7 更新

- 快速记录页，支持 30 秒保存项目
- Demo 深度评估默认折叠
- 竞品候选和正式竞品录入默认折叠
- 历史记录默认折叠，默认只显示最近 10 条
- 页面改为快速记录、Demo 试玩、竞品与候选、历史与导出、文档与状态分层

## V0.31 更新

- 新增搜索中心 / Search Center 页面
- 根据游戏名、Steam URL、简介、标签、关键词、参考游戏、开发商、发行商生成 keyword_set
- 生成竞品搜索表和全平台声量搜索表
- 只生成搜索链接和人工填写字段，不真实爬取任何平台
- 导出 UTF-8-SIG CSV 到 `exports/`

## V0.31a 更新

- 搜索中心每个关键词提供 Google、百度、Steam、SteamDB、YouTube、B站、Reddit、itch、IGDB 快捷打开入口
- 增加国内搜索优先组和海外搜索优先组
- 支持勾选链接后批量打开，超过 10 个默认限流并要求确认
- 只打开搜索页，不做浏览器自动化、不爬取、不读取搜索结果

## V0.31b 更新

- 搜索中心移除 A/B/C 调试式标题，改为 6 个清晰分区
- 新增平台字典 `config/search_platforms.json`
- 补充 TapTap、贴吧、NGA、小黑盒、游侠、游民星空、巴哈姆特、X、Bluesky 等小平台
- 明确原生搜索、百度站内搜索、Google 站内搜索和手动平台说明
- URL 默认隐藏到“显示完整链接”，页面以平台名、搜索词、搜索类型和打开按钮为主
- 批量打开链接默认折叠，并按 Steam/商业、国内声量、海外声量、站内搜索兜底筛选

## V0.31c 更新

- 平台字典增加区域策略：`mainland_cn`、`hk_tw`、`global` 等
- 国内平台默认百度站内搜索，Google 作为备用
- 巴哈姆特归入港澳台社区搜索，默认 Google 站内搜索，百度备用
- Steam、SteamDB、YouTube、Reddit、X、Bluesky 等海外/全球平台不默认显示百度
- 搜索导航按“平台 + 关键词”合并展示，推荐和备用搜索按钮在同一行
- 增加“显示备用搜索引擎”开关，完整 URL 仍默认折叠

## V0.31d 更新

- 搜索中心顶部增加摘要区，优先展示 keyword_set 数量、导航总数和推荐入口数量
- 默认展开“推荐优先搜索”，只展示高优先级平台和核心关键词
- 增加精简模式、标准模式、完整模式，避免默认铺开 300+ 条导航
- 搜索分区默认折叠，分区标题显示总数量和当前显示数量
- 分区内按平台分组，并按核心关键词优先展示
- 批量打开链接默认关闭，进入后先选择推荐、分区、平台或全部范围
- 保留 `exports/search_navigation_links.csv`，新增 `exports/search_navigation_recommended.csv`

## V0.31e 更新

- 启动脚本启动前检查 `8501` 端口，发现旧服务会尝试关闭旧 PID
- `启动_项目初筛助手.bat`、`启动_最小化.bat`、`start_app.bat` 统一使用 `--server.port 8501`
- `停止_项目初筛助手.bat` 只查找并关闭占用 `8501` 端口的 PID，不会杀所有 Python
- 侧边栏增加退出提醒：关闭网页不等于退出后台服务
- 启动失败时提示先运行 `停止_项目初筛助手.bat`

## V0.4 更新

- 新增“一键项目画像”Tab
- 支持 Steam URL/AppID 输入，并自动解析 AppID
- 新增 Steam 商店公开信息提取，失败时提示“自动获取失败，请手动补充”，不阻断页面
- 新增规则化画像生成：基础信息、核心玩法初判、可能卖点、可能竞争点、中国区发行机会、主要风险、建议下一步、人工确认清单
- 支持保存为项目记录；同 AppID 已存在时先提示，当前先支持追加为新记录
- 支持生成 `reports/profile/` 下的 Markdown/txt 画像报告
- 支持联动搜索中心关键词和竞品候选发现器输入
- 不接入 AI API，不接入 Steam 评论工具，不做复杂爬虫

## V0.4.1 更新

- 项目画像页面改为结论先行，新增快速结论卡片
- 快速结论卡片压缩展示初步类型、核心循环、卖点、竞争点、中国区机会、风险和下一步建议
- 完整卖点、竞争点、风险和人工确认清单默认放入折叠区
- 画像 Markdown/txt 报告改为“0. 快速结论”开头
- 新增 Steam 竞品候选自动查找，只抓 Steam 搜索结果，不抓全网搜索结果
- 候选只写入 `data/competitor_candidates.csv`，不自动进入正式竞品表
- 新增 `data/cache/steam_competitor_search_cache.json`，24 小时内同 AppID + keyword 复用缓存
- 请求失败时提示使用搜索中心手动查找，不阻断画像功能

## V0.4.2 更新

- 画像快速结论进一步压缩，减少重复安全提示
- 新增类型信号提取模块，优先识别 roguelite deckbuilder、card battler、卡牌肉鸽、卡组构筑等高价值短语
- 新增外部标题线索模块，支持从 B站/YouTube/百度/Google/小黑盒等标题中提取类型词和类比游戏
- 一键画像页面支持手动粘贴外部标题，也支持轻量自动抓取标题，失败不阻断
- Steam 竞品候选关键词从宽泛标签搜索改为“核心类型短语 + 外部类比词 + 强标签组合”
- 候选新增 `match_score` 和 `match_level`，默认只展示高/中匹配
- 卡牌肉鸽项目会降低 Heroes of Might and Magic、Warhammer 40K、Age of Wonders 等偏离策略结果优先级
- 画像报告加入类型信号来源、外部标题线索和推荐竞品方向

## V0.4.3 更新

- 快速结论首屏顺序改为：游戏类型、核心循环、竞品锚点、主卖点、中国区机会、主要风险、下一步
- 原竞品方向字段下线，改为“竞品锚点 / 相似参考”
- “竞品比较维度”独立展示在完整竞争点分析折叠区
- Cardoom 画像显示为卡牌肉鸽 / Roguelite Deckbuilder / Card Battler
- 弹幕幸存者类项目显示为弹幕幸存者 / 逆弹幕射击 / 轻度 Rogue
- 画像报告同步改为“竞品锚点与比较维度”

## V0.5 更新

- 新增“SteamDB 发现”Tab，作为常用 SteamDB 发现入口工作台
- 常用入口覆盖 Top Rated Releases、Charts、Trending Followers、Wishlist Activity、Most Wishlisted、Upcoming、Calendar
- 新增 SteamDB 筛选模板保存：`data/steamdb_link_templates.csv`
- 新增 SteamDB 榜单观察记录：`data/steamdb_watch_notes.csv`
- 支持解析 SteamDB App 链接或 AppID，并生成 Steam 商店页、SteamDB App、Charts、History、Depots、Subs、Patchnotes 快捷入口
- 支持将观察记录或快速导入项目发送到一键项目画像、搜索中心，或保存为快速项目记录
- Excel 导出新增 `SteamDB观察` 和 `SteamDB模板` sheet
- 本版本不自动爬 SteamDB 榜单，不使用 Selenium，不依赖 SteamDB 公开页面以外的接口

## V0.5.1 更新

- 新增 `启动_无窗口.vbs`，作为日常无窗口启动入口
- 新增 `启动_后台服务.bat`，由 VBS 后台调用，不要求用户直接查看窗口
- 后台启动前检查 `8501` 端口，只关闭占用该端口的 PID，不批量杀 Python
- 新增 `查看_服务状态.bat`，显示服务是否运行和 PID
- 更新 `停止_项目初筛助手.bat`，继续只关闭 `8501` 端口上的后台服务
- 后台启动日志输出到 `logs/streamlit.log`
- 原 `启动_项目初筛助手.bat` 保留为调试入口

## V0.5.2 更新

- 新增 `首页 / 今日看板` Tab，并放在所有 Tab 最前面
- 首页聚合今日快捷入口、SteamDB 发现入口、Steam / 新闻 / 活动入口
- 首页读取 `data/projects.csv`，展示最近项目和待处理项目
- 新增 `data/daily_watch_notes.csv`，支持记录今日观察
- 今日观察可保存后发送到一键项目画像或搜索中心
- 首页顶部展示今日观察数、待处理项目数、最近 7 天新增项目数、当前候选竞品数
- Excel 导出新增 `今日观察` sheet
- 本版本不爬 SteamDB 榜单，不爬 Steam 首页，不接入 AI API

## V0.5.3 更新

- 首页改为“今日发行观察”信息流，不再以入口按钮为首屏主体
- 新增 `modules/home_feed_fetcher.py`，轻量获取 SteamDB 热门在线、Trending Followers、Wishlist / Upcoming 和 Steam 新闻
- 新增 `data/cache/home_feed_cache.json`，缓存首页信息流，默认读缓存，手动刷新才请求
- 首页首屏展示重点榜单卡片、今日发现项目、Steam 新闻与活动摘要
- 信息流项目支持加入今日观察、发送到项目画像、发送到搜索中心、加入候选池
- 网络失败时不崩溃，显示入口按钮、缓存数据或本地最近项目兜底
- 最近项目和待处理项目保留，但下移为辅助区

## V0.5.4 更新

- 首页首屏改为“今日项目卡片”，优先读取 `daily_watch_notes.csv`、`steamdb_watch_notes.csv`、`projects.csv` 和 feed 缓存
- 新增 Steam 图片缓存 `data/cache/steam_images_cache.json`，AppID 图片使用 Steam appdetails 轻量获取并缓存 7 天
- 自动抓取失败信息下移到“数据获取状态 / 调试信息”折叠区，首页主体不再显示失败黄块
- 外部入口统一使用 `st.link_button`，Steam、SteamDB、Steam News、Specials、Upcoming Events 和常用 SteamDB 榜单入口可直接打开
- 首页项目卡的“项目画像”和“搜索中心”会写入 `session_state` 预填目标页面字段，并在首页顶部显示目标 Tab 提示
- 今日观察记录表单默认折叠，保留保存、保存并发送到项目画像、保存并发送到搜索中心
- 无自动数据和本地记录时显示 Top Rated Releases、Trending Followers、Wishlist Activity 三张入口卡

## V0.5.5 更新

- 首页首屏改为“今日新项目发现”，优先展示新项目、热点项目、即将推出项目和首页快照
- 新增首页快照 CSV：`data/home_snapshots.csv`
- 新增快照图片目录：`data/snapshots/`
- 首页快照支持上传本地图片、填写图片 URL、来源链接、Steam 链接、SteamDB 链接、标题、副标题、备注、下一步动作和 priority
- 首页快照卡片支持打开来源、打开 Steam、打开 SteamDB、项目画像预填、搜索中心预填、加入今日观察和归档
- 新增快照管理折叠区，支持显示已归档、按来源筛选、按游戏名搜索、归档 / 恢复和 priority 调整
- 图片显示优先级为本地上传图片、远程图片 URL、Steam 图片缓存、Steam appdetails 图片、占位入口卡
- 抓取失败信息继续只在“数据状态 / 调试信息”折叠区展示，首页主体不显示失败黄块
- 本地最近项目与待办下移为工作续接区，默认各显示 5 条
- Excel 导出新增 `首页快照` sheet

## V0.5.6 更新

- 新增 Steam 图文源模块：`modules/steam_store_feed_fetcher.py`
- 首页使用 Steam `search/results` 获取 Steam 新品趋势、即将推出、热销趋势和折扣热点项目
- 新增 Steam 图文源缓存：`data/cache/steam_home_feed_cache.json`，有效期 30 分钟
- 首页首屏优先展示真实 Steam 游戏卡片，包含图片、游戏名、来源、价格、发售日期、评价摘要和 AppID
- 图片优先使用 Steam 搜索结果图片，缺失时复用 Steam 图片缓存 / appdetails 补图
- Steam 游戏卡支持打开 Steam、打开 SteamDB、项目画像预填、搜索中心预填、加入今日观察和加入候选
- 首页增加来源筛选、隐藏热销/折扣大作、只看即将推出、只看 Demo、只看简中
- SteamDB 自动抓取不再作为首页主体依赖，只保留常用入口卡
- 首页快照保留为人工补充，本地最近项目继续下移
- Excel 导出新增 `首页Steam图文源` sheet

## V0.5.7 更新

- 新增 Steam appdetails 详情缓存：`data/cache/steam_appdetails_cache.json`
- 首页只对当前 Steam 图文卡前 12-20 个 AppID 做详情补全，避免高频请求
- Steam 图文卡显示开发商、发行商、发售日期、类型、价格、简中支持和 Demo 状态
- 卡片详情折叠区显示标签、评价摘要、语言摘要、Steam 上架日期 / 页面创建日期和获取状态
- Steam 上架日期 / 页面创建日期在 appdetails 拿不到时显示“未获取”，并标注后续通过 SteamDB History 或人工摘录补充
- 首页标题改为“今日新游雷达”
- 来源筛选显示数量，并隐藏无数据来源
- 删除“待查看”入口卡，Steam / SteamDB 入口改为折叠区紧凑按钮
- 项目画像和搜索中心联动补充 developer、publisher、genres、release_date 等字段
- Excel `首页Steam图文源` sheet 增加详情补全字段

## V0.5.8 更新

- 修复 appdetails 获取方式，去掉限制性 filters，确保 developers、publishers、genres、categories、price_overview 等字段能返回
- 修复 developers / publishers 字段解析，分别用 ` / ` 拼接为开发商和发行商
- 旧 appdetails 缓存如果缺 schema 或关键字段，会自动重新获取并标记状态
- 新增“刷新当前卡片详情”按钮，支持忽略旧缓存刷新当前展示卡片详情
- 首页来源分组纠偏，不再使用“新品趋势”作为展示来源
- 来源分组改为即将推出、近期上架、热销 / 热门趋势、折扣热点
- 老游戏和已发行大作默认从即将推出 / 近期上架降权到热销 / 热门趋势
- 来源筛选显示数量，并只显示有数据来源
- 首页Steam图文源导出字段补全 source_group、search_source_filter、developer、publisher、genres、categories、price、supports_schinese、has_demo、appdetails_status、cache_status

## V0.5.9 更新

- 根目录启动入口统一为 `启动工具.vbs`、`停止工具.bat`、`查看状态.bat`、`调试启动.bat`
- 旧启动、停止、状态和环境导出 bat/vbs 已归档到 `tools/legacy_launchers/`
- `启动工具.vbs` 后台调用 `tools/launchers/run_streamlit_hidden.bat`，无 cmd 窗口启动 Streamlit 并打开 `http://localhost:8501`
- 隐藏启动日志写入 `logs/streamlit.log`
- `停止工具.bat` 只查找并关闭占用 `8501` 端口的 PID，不会杀所有 Python
- `查看状态.bat` 只显示 `8501` 是否运行和 PID，不做关闭操作
- `调试启动.bat` 保留可见 cmd 窗口，方便查看启动报错
- 新增 `启动说明.txt`

## 当前数据文件

- `data/projects.csv`
- `data/competitors.csv`
- `data/competitor_candidates.csv`
- `data/steamdb_link_templates.csv`
- `data/steamdb_watch_notes.csv`
- `data/daily_watch_notes.csv`
- `data/home_snapshots.csv`
- `data/snapshots/`
- `data/cache/steam_home_feed_cache.json`
- `data/cache/steam_appdetails_cache.json`
- `data/cache/home_feed_cache.json`
- `data/cache/steam_images_cache.json`
- `data/cache/steam_competitor_search_cache.json`

## 当前报告目录

- `reports/markdown/`
- `reports/txt/`
- `reports/excel/`
- `reports/profile/`

## 当前启动文件

- `启动工具.vbs`
- `停止工具.bat`
- `查看状态.bat`
- `调试启动.bat`

旧启动脚本归档目录：

- `tools/legacy_launchers/`

## V0.6.2 状态

- 一键项目画像已收敛为最小可用版：输入 Steam 链接或 AppID 后生成紧凑发行初筛页。
- 页面保留基础信息、商店图文预览、发行判断卡和 Markdown 预览。
- Steam 评测摘要加入好评率、评测数、评测样本平均/中位游玩时间。
- 冗余模板分析和竞品候选区不再默认显示。

## V0.6.2b 状态

- 项目画像页的发行判断卡已改为项目初筛卡。
- 增加 data_quality_level，用于区分 high / medium / low 数据充分性。
- 无评测或核心素材不足时，页面和 Markdown 明确提示不能做发行判断。
- Markdown 快速结论同步改为快速初筛。

## V0.6.3 状态

- 首页 Steam 图文卡优先使用 appdetails / normalized 字段。
- 首页来源分组改为即将推出、近期上架、热销参考、手动观察。
- 刷新当前卡片详情后会重新合并 appdetails 字段。
- 卡片详情增加 card_data_source、last_detail_fetched_at、feed_fetched_at 等调试字段。

## V0.6.4 状态

- 首页顶部新增 Steam 快速搜索入口。
- 支持游戏名、AppID、Steam 链接和 SteamDB app 链接直查。
- 搜索结果复用首页图文卡，可发送到项目画像、搜索中心、观察和候选。
- 搜索调试信息接入现有数据状态区。

## V0.6.4a 状态

- 首页顶部新增 Steam 直查入口。
- 支持 AppID、Steam app 链接和 SteamDB app 链接。
- 直查结果生成单张图文卡，字段来自 appdetails / normalized card。
- 直查卡可发送到一键项目画像。

## V0.6.5 状态

- 一键项目画像新增外部情报手动记录区，默认折叠。
- 支持公开视频、社区、官网、Presskit 等人工来源。
- 项目画像页汇总外部声量、中文侧内容、官网/Presskit 和社群入口。
- Markdown 报告加入“外部声量与资料”，导出 Excel 新增“外部情报” sheet。

## V0.6.6 状态

- 一键项目画像内新增“外部情报库 / 管理”折叠区。
- 支持按 AppID、游戏名、平台、相关度、情绪和证据类型过滤。
- 支持选择 record_id 编辑、删除和按 source_url 规则去重。
- 当前项目情报可单独导出到 `exports/external_intel_*.csv`。

## V0.6.7 状态

- 首页今日观察历史按创建时间倒序显示，并支持刷新和二次确认清空。
- 首页卡片字段合并改为 appdetails / normalized / 本地记录 / 未获取优先级。
- 所有发送到项目画像入口统一写入预填字段。
- 外部情报保存增加疑似重复提示，首页新增数据健康检查区。

## V0.6.9 状态

- 首页新增快速收录项目入口。
- 可从 Steam / SteamDB / 社媒链接 / 备注解析项目基础信息。
- 支持保存项目记录、外部情报并发送到一键项目画像。
- 工具定位收口为外部发现后的记录与画像生成器。

## V0.6.11a 状态

- 启动工具只由 VBS 打开一次 `http://localhost:8501`，Streamlit 后台以 headless 模式运行。
- 开发商本体调查和第三方市场数据表单改为常用字段优先、低频字段折叠。
- VGI / Gamalytic 入口改为主页加搜索词复制，当前市场数据仍为手动录入。
V0.6.11a-hotfix：修复启动工具只打开浏览器但未启动 Streamlit 服务的问题。
启动流程恢复为先启动服务、等待 localhost:8501 可访问、再由 VBS 只打开一次浏览器。
保留 调试启动.bat 用于可见窗口启动并查看错误。

## V0.6.11a-launch-cleanup 状态

- 弃用 VBS 隐藏启动。
- 启动入口收敛为 启动工具.bat / 停止工具.bat / 运行本地验收.bat / 调试启动.bat。
- 修复启动项过多和 VBS 字符串错误导致的启动失败。

## V0.6.11a 状态

- 压缩开发商本体调查表单。
- 压缩第三方市场数据录入表单。
- 修复 VGI / Gamalytic 错误入口。
- 明确第三方市场数据当前为手动记录模式。

## V0.6.11c 状态

- 首页主入口调整为“查查 / Steam 项目直查”，今日新游雷达位于查查下方。
- 新增 `data/search_history.csv`，查查历史独立于正式项目库。
- 历史项目记录支持发送到查查、发送到项目画像、打开 Steam / SteamDB 和复制关键字段。
- Steam appdetails 增加 default / us / jp / hk / tw fallback，并补充单 AppID 商店页 HTML fallback。
- 项目画像改为基础信息后直接显示商店图文预览。
## V0.6.11c-hotfix

- 查查普通文本搜索改为低信任候选：主候选只显示高相关或本地精确匹配，低相关候选默认折叠。
- 候选卡片补充 appdetails 图文预览、相关性评分和匹配原因。

## V0.6.12

- 项目画像新增 Steam 动态 / 公告面板，位于商店图文预览之后、项目初筛卡之前。
- Steam News 支持 6 小时本地缓存、手动刷新和 Markdown 导出章节。

## V0.6.12-hotfix

- Steam 动态摘要改为清洗后文本，去除 HTML/BBCode/转义符和纯链接噪声。
- Markdown/TXT 导出兼容 Steam 动态参数，避免报告生成 TypeError。

V0.6.12-hotfix2：修复 Markdown 图像报告导出时 steam_news_result 参数不兼容导致的 TypeError。

## V0.6.13

- 项目画像新增 Steam 评论预览，位于 Steam 动态之后、项目初筛卡之前。
- 支持最近评论、有价值评论、最近差评少量样本展示，并写入 Markdown 图像报告。

## V0.6.14a

- 全局页面减负完成：低频表单、调试信息、缓存路径默认折叠，高频入口保持可见。
- SteamDB 发现、搜索中心、Demo 试玩、竞品与候选页面已按日常工作流整理默认展示。
- 项目画像模块顺序不变，Steam 动态、评论预览、开发商调查、第三方市场和外部情报改为按需展开。
