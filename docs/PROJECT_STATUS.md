# PROJECT_STATUS

## 当前项目状态

- 项目名称：Steam 项目初筛助手
- 当前版本：V0.6.1b 项目画像商店图文预览
- 当前定位：本地 Steam 项目初筛工作台

## 当前已完成

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
- 本版本不自动爬 SteamDB 榜单，不使用 Selenium，不依赖 SteamDB 非公开 API

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
