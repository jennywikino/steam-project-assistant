# CHANGELOG

## V0.6.11

- 新增第三方市场数据记录卡，支持 VGI / Gamalytic / SteamDB / SteamSpy / Steam官方手动录入。
- 项目画像新增市场数据摘要和来源对比。
- Markdown 报告新增第三方市场数据节。
- 预留未来 API 配置模板 `config/data_sources.example.json`。

## V0.6.10a

- 修复多发行商只搜索第一个的问题。
- 开发商/发行商名称统一拆分，支持分别搜索每个开发商/发行商。
- 公司档案保存时按单个公司名和角色保存。

## V0.6.10

- 新增开发商本体调查窗口，放在项目画像基础信息下方。
- 支持记录公司/团队资料、联系方式、作品、发行合作史和人工证据。
- 生成外部搜索入口，项目画像报告新增“开发商本体调查”节。
- 新增 `data/company_dossier.csv` 本地公司档案。

## V0.6.1b

- 一键项目画像新增商店图文预览。
- 展示 header 图、截图、视频缩略图和短描述。
- 增加非 AI 的视觉初判提示，复用 Steam appdetails 数据。

## V0.6.0

- 新增 Steam 评价摘要模块 `modules/steam_review_stats.py`，使用 Steam appreviews 一页摘要和评测样本游玩时间，写入 12 小时缓存 `data/cache/steam_review_stats_cache.json`。
- 首页 Steam 图文卡新增好评率、评测数、评测摘要、评测样本中位/平均游玩时间，并标注游玩时间基于 Steam 评测样本。
- 首页筛选新增好评率、评测数、游玩时间中位数、当前折扣、价格和“严格筛选已获取字段”。
- 新增 `modules/steam_data_normalizer.py`，统一首页、项目画像、搜索中心联动的 Steam 基础字段和评价字段。
- 一键项目画像页优先读取首页传入的 developer、publisher、genres、release_date、price 和评价数据，再补缓存详情。
- 项目画像页清理“完整中国区机会”“完整竞争点分析”“完整风险与人工确认清单”等泛标题，改为紧凑发行判断卡和实用展开区。
- 首页新增 IndieNova 风格“常用工具”小方块入口：SteamDB、Steam 折扣、Top Rated、Wishlist、Followers、Calendar、B站搜索、小黑盒搜索、项目画像、搜索中心。
- Excel `首页Steam图文源` sheet 新增 review_total、review_positive、review_negative、positive_rate、review_score_desc、sample_review_count、median_playtime_hours、avg_playtime_hours、review_stats_status。

## V0.1

- 项目基础卡
- CSV 保存
- Markdown/txt 报告

## V0.2

- Demo 试玩记录字段

## V0.2.1

- 历史记录
- 中文列名
- Excel 导出

## V0.3

- 竞品对照表

## V0.3.5

- 竞品候选发现器

## V0.3.6

- 可用性修复
- 历史折叠
- 软删除
- 搜索链接修复
- 启动方式优化

## V0.3.7

- 表单减负
- 快速记录页
- 深度评估折叠
- 历史记录折叠和最近 10 条默认展示
- 支持 30 秒保存项目

## V0.31

- 新增搜索中心 / Search Center
- 半自动生成竞品搜索链接
- 半自动生成全平台声量搜索链接
- 支持 We Need An Army 示例输入
- 支持导出 `exports/competitor_search_links.csv`
- 支持导出 `exports/platform_presence_search_links.csv`
- 不接入 YouTube、IGDB、B站、SteamDB 等 API 或爬虫

## V0.31a

- 搜索中心增加浏览器打开搜索链接功能
- 增加百度搜索链接
- 增加国内搜索优先组：百度、B站、小黑盒、游民星空、游侠
- 增加海外搜索优先组：Google、Steam、SteamDB、YouTube、Reddit、itch、IGDB
- 支持勾选链接后批量打开，默认限制 10 个标签页
- 不新增 Playwright、Selenium，不读取搜索结果

## V0.31b

- 修正搜索中心 A/B/C 标题不清晰问题
- 新增 `config/search_platforms.json` 平台字典
- 补充 TapTap、贴吧、小黑盒、游侠、游民星空、巴哈姆特、X、Bluesky 等平台入口
- 补充 NGA 玩家社区，使用百度/Google 站内搜索兜底
- 明确百度/Google 站内搜索兜底说明，避免误解为平台原生搜索
- 搜索中心改为平台导航式展示，默认折叠分区，不直接展示长 URL
- 批量打开链接默认折叠，并改为先按平台分类筛选

## V0.31c

- 为搜索平台字典增加 `region`、`preferred_engines`、`fallback_engines` 策略字段
- 国内平台默认使用百度站内搜索，并保留 Google 作为备用搜索
- 巴哈姆特归入港澳台社区搜索，默认使用 Google 站内搜索，百度只作为备用
- 海外平台和全球平台默认使用平台原生搜索或 Google，不默认显示百度
- 搜索结果按“平台 + 关键词”合并成一行，同一行内提供推荐和备用搜索按钮
- 增加“显示备用搜索引擎”开关，默认只展示推荐搜索

## V0.31d

- 搜索中心增加摘要区，优先显示 keyword_set、导航总数、推荐入口和平台数量
- 新增推荐优先搜索区，默认展开 8-12 条高优先级入口
- 新增精简模式、标准模式、完整模式，默认使用精简模式
- 分区默认折叠，标题显示总数量和当前显示数量
- 分区内按平台分组，默认只展示核心关键词
- 批量打开链接默认只显示推荐优先链接，可手动切换到分区、平台或全部链接
- 保留全量 CSV 导出，并新增 `exports/search_navigation_recommended.csv`

## V0.31e

- 启动脚本启动前自动检查并清理旧的 8501 端口进程
- 增强 `启动_项目初筛助手.bat`、`启动_最小化.bat`、`start_app.bat`
- 增强 `停止_项目初筛助手.bat`，只关闭 8501 端口上的服务
- 侧边栏增加“退出提醒”，说明关闭浏览器不等于退出程序
- 文档补充启动失败时先运行停止脚本的排障说明

## V0.4

- 新增“一键项目画像”Tab
- 支持 Steam URL/AppID 输入，并从 Steam URL 自动解析 AppID
- 新增 `modules/steam_store_fetcher.py`，尝试获取 Steam 商店公开信息
- 新增 `modules/project_profile_generator.py`，用规则生成项目画像草稿
- 画像草稿包含基础信息、核心玩法初判、可能卖点、可能竞争点、中国区发行机会、主要风险、建议下一步、人工确认清单
- 支持保存画像摘要到 `data/projects.csv`，同 AppID 已存在时先提示，V0.4 支持追加为新记录
- 新增 `reports/profile/`，支持生成 Markdown/txt 画像报告
- 支持发送画像关键词到搜索中心并生成搜索入口
- 支持发送画像标签和关键词到竞品候选发现器
- 不接入 AI API，不接入 Steam 评论工具，不做复杂爬虫

## V0.4.1

- 压缩“一键项目画像”页面展示，新增快速结论卡片
- 快速结论卡片包含初步类型、核心循环一句话、主要卖点、主要竞争点、中国区机会、主要风险、主建议和备用建议
- 画像 Markdown/txt 报告改为先短后长，新增“0. 快速结论”
- 新增 `modules/steam_competitor_finder.py`
- 支持从 Steam 搜索页自动查找竞品候选，不抓 B站、YouTube、小黑盒、Google 结果
- 每次根据目标项目生成 3-5 个关键词，每个关键词最多取前 10 条，总候选最多 30 条
- 自动排除目标游戏本身，并按 AppID 去重
- 支持把候选写入 `data/competitor_candidates.csv`，默认“待确认”，排除时写入“排除”
- 不自动写入正式竞品表 `data/competitors.csv`
- 新增 `data/cache/steam_competitor_search_cache.json`，同 AppID + keyword 24 小时内优先使用缓存

## V0.4.2

- 进一步压缩画像文案，快速结论卡片改为发行初筛短句
- 新增 `modules/genre_signal_extractor.py`，从 short_description、about_the_game、genres、tags、用户关键词和外部标题线索提取类型信号
- 新增 `modules/external_title_clue_extractor.py`，支持从粘贴标题中提取卡牌肉鸽、杀戮尖塔、小丑牌、炉石等线索
- 一键画像页面新增“外部标题线索，可选”和“尝试抓取外部标题线索”
- Steam 竞品候选搜索改为优先使用核心类型短语和外部类比词，不再单独用 Strategy / Turn-Based Tactics 等泛标签触发搜索
- 新增候选 `match_score` 和 `match_level`
- 默认只展示高/中匹配候选，低匹配候选放入折叠区
- 针对卡牌肉鸽/卡组构筑项目降低大型 IP 策略、4X、传统战棋等偏离结果优先级
- 画像报告新增类型信号来源、外部标题线索和推荐竞品方向

## V0.4.3

- 修正快速结论卡片字段语义
- 类型字段改为“游戏类型 / 赛道定位”
- 原竞品方向字段拆分为“竞品锚点 / 相似参考”和“竞品比较维度”
- 竞品锚点只展示具体相似游戏或明确赛道锚点，不再混入价格、内容量、完成度等比较标准
- 竞品比较维度移入“展开查看完整竞争点分析”
- 增加弹幕幸存者、殖民地模拟、银河城、城市建造等赛道定位规则
- 项目画像报告同步改为“竞品锚点与比较维度”

## V0.5

- 新增“SteamDB 发现”Tab，定位为 SteamDB 发现工作台
- 固化 Top Rated Releases、Charts、Trending Followers、Wishlist Activity、Most Wishlisted、Upcoming、Calendar 等常用入口
- 新增 `data/steamdb_link_templates.csv`，支持保存自定义 SteamDB 筛选链接和活动链接
- 新增 `data/steamdb_watch_notes.csv`，支持手动记录榜单观察项目
- 支持解析 SteamDB App 链接或 AppID，并生成 Steam / SteamDB 单 App 快捷入口
- 支持将 SteamDB 观察或快速导入项目发送到一键项目画像、搜索中心，或保存为快速项目记录
- Excel 导出新增 `SteamDB观察` 和 `SteamDB模板` sheet
- 不自动爬 SteamDB 榜单，不依赖 SteamDB 非公开 API，不使用 Selenium

## V0.5.1

- 新增 `启动_无窗口.vbs`，日常启动不显示 cmd 窗口
- 新增 `启动_后台服务.bat`，供 VBS 后台启动 Streamlit
- 后台启动前检查 `8501` 端口，只关闭占用该端口的 PID
- 后台日志输出到 `logs/streamlit.log`
- 新增 `查看_服务状态.bat`，显示 `8501` 是否运行和对应 PID
- 更新 `停止_项目初筛助手.bat` 文案，继续只关闭 `8501` 端口 PID
- README 和排障文档补充无窗口启动、停止、状态检查说明

## V0.5.2

- 新增 `首页 / 今日看板` Tab，并放在所有 Tab 最前面
- 首页聚合今日快捷入口、SteamDB 常用入口、Steam / News / 活动入口
- 首页读取最近项目和待处理项目，长表格默认放入折叠区
- 新增 `data/daily_watch_notes.csv`，支持保存今日观察记录
- 今日观察支持保存后发送到一键项目画像或搜索中心
- 首页顶部新增今日观察数、待处理项目数、最近 7 天新增项目数、当前候选竞品数
- Excel 导出新增 `今日观察` sheet
- 本版本不爬 SteamDB 榜单，不爬 Steam 首页，不接入 AI API

## V0.5.3

- 首页从入口导航页改为“今日发行观察”信息流首页
- 新增 `modules/home_feed_fetcher.py`，轻量获取 SteamDB Charts、Trending Followers、Wishlist / Upcoming 和 Steam 新闻
- 新增 `data/cache/home_feed_cache.json`，首页信息流缓存 30 分钟，刷新按钮带短时间防重复请求
- 首页首屏展示重点榜单卡片、今日发现项目、Steam 新闻与活动摘要
- 自动获取失败时显示入口按钮，并优先显示缓存或本地最近项目兜底
- 信息流项目支持加入今日观察、发送到一键项目画像、发送到搜索中心和加入候选池
- 最近项目和待处理项目保留，但下移为辅助区

## V0.5.4

- 首页新增视觉项目卡片，优先使用今日观察、SteamDB 观察、本地项目和缓存 feed 生成首屏内容
- 新增 `modules/steam_image_cache.py` 和 `data/cache/steam_images_cache.json`，按 AppID 缓存 Steam appdetails 图片 7 天
- 首页外部入口统一使用 `st.link_button`，Steam、SteamDB、Steam News、Specials、Upcoming Events、Charts、Trending Followers、Wishlist Activity、Top Rated Releases、Calendar 都可直接跳转
- 自动抓取失败信息不再占据首页主体，只在“数据获取状态 / 调试信息”折叠区展示
- 首页项目卡支持预填一键项目画像和搜索中心，并在页面顶部显示目标 Tab 提示
- 今日观察记录表单改为默认折叠，保留保存、保存并发送到项目画像、保存并发送到搜索中心
- 无自动数据和本地记录时显示 3 张默认 SteamDB 入口卡，不再显示“获取失败”黄块

## V0.5.5

- 首页首屏改为新项目发现优先，不再优先展示 `projects.csv` 本地最近项目
- 新增 `data/home_snapshots.csv`，支持首页快照卡片记录、补列和 UTF-8-SIG 保存
- 新增 `data/snapshots/` 图片目录，支持用户上传快照图片并在首页卡片显示
- 首页卡片来源优先级调整为：首页快照、今日观察、SteamDB 观察、SteamDB / Steam feed 缓存、默认入口卡
- 首页默认入口卡扩展为 Top Rated Releases、Trending Followers、Wishlist Activity、Upcoming / Calendar
- 首页卡片支持打开来源、打开 Steam、打开 SteamDB、项目画像、搜索中心、加入观察和快照归档
- 新增“添加首页快照”和“管理首页快照”折叠区，支持快照归档 / 恢复、来源筛选、游戏名搜索和 priority 调整
- 抓取失败信息继续只放入“数据状态 / 调试信息”折叠区，首页主体显示快照卡或入口卡
- 本地最近项目与待办下移为工作续接区，默认各显示 5 条，完整表放入折叠区
- Excel 导出新增 `首页快照` sheet

## V0.5.6

- 新增 `modules/steam_store_feed_fetcher.py`，从 Steam `search/results` 获取图文项目源
- 新增 `data/cache/steam_home_feed_cache.json`，Steam 图文源缓存 30 分钟，首页默认读缓存，点击“刷新 Steam 图文源”才重新请求
- 首页首屏优先展示真实 Steam 游戏图文卡，不再把空入口卡放在自动游戏卡之前
- Steam 图文源覆盖 Steam 新品趋势、Steam 即将推出、Steam 热销趋势、Steam 折扣热点
- Steam 游戏卡显示图片、游戏名、来源分组、价格、发售日期、评价摘要、AppID，并支持打开 Steam、打开 SteamDB、项目画像、搜索中心、加入今日观察、加入候选
- 首页增加来源筛选、隐藏热销/折扣大作、只看即将推出、只看 Demo、只看简中等轻量筛选
- SteamDB 自动抓取不再作为首页主体依赖，首页仅保留 Top Rated Releases、Trending Followers、Wishlist Activity、Most Wishlisted、Upcoming、Calendar 入口卡
- 首页快照卡片保留但下移为人工补充，本地最近项目继续下移为工作续接
- Excel 导出新增 `首页Steam图文源` sheet

## V0.5.7

- 新增 `modules/steam_appdetails_cache.py`，以 AppID 缓存 Steam appdetails 详情 7 天
- 首页 Steam 图文卡补全开发商、发行商、类型、价格、发售日期、简中支持、Demo 状态和详情获取状态
- Steam 上架日期 / 页面创建日期不再用发售日期替代，appdetails 拿不到时统一显示“未获取”
- 首页标题改为“今日新游雷达”，副标题压缩为新游筛选导向
- 来源筛选改为只显示有数据来源，并展示数量，例如“即将推出（8）”
- 只看 Demo / 只看简中筛选只保留明确为“是”的项目，筛选为空时提示放宽筛选
- 删除首页主体中的“待查看”入口卡，Steam / SteamDB 常用入口改为折叠区紧凑按钮
- 项目画像和搜索中心联动补充 developer、publisher、genres、release_date 等字段
- `首页Steam图文源` Excel sheet 新增 developer、publisher、steam_page_date、genres、tags、has_demo、supports_schinese、detail_fetch_status 等字段

## V0.5.8

- 修复 appdetails 补全：改为无 filters 获取公开详情，确保 developers / publishers / genres 等字段可解析
- 详情缓存新增 schema 检查，旧缓存缺 developers / publishers / genres 时自动重新获取
- 新增“刷新当前卡片详情”按钮，可忽略旧 appdetails 缓存重新获取当前展示卡片详情
- 首页来源分组纠偏：移除“新品趋势”，改为“即将推出 / 近期上架 / 热销 / 热门趋势 / 折扣热点”
- 旧缓存中的 `Steam 新品趋势`、`Steam 热销趋势` 等旧分组会自动映射到新分组
- Counter-Strike 2、Apex Legends、Dota 2、PUBG、GTA V、Rust、Wallpaper Engine 等老游戏默认从“即将推出 / 近期上架”降权到“热销 / 热门趋势”
- 来源筛选继续显示数量，并只展示有数据来源
- 首页Steam图文源导出字段补全 source_group、search_source_filter、developer、publisher、genres、categories、price、supports_schinese、has_demo、appdetails_status、cache_status

## V0.5.9

- 统一根目录启动入口，只保留 `启动工具.vbs`、`停止工具.bat`、`查看状态.bat`、`调试启动.bat`
- 旧 bat/vbs 启动相关脚本归档到 `tools/legacy_launchers/`
- 新增内部隐藏启动脚本 `tools/launchers/run_streamlit_hidden.bat`
- 日常启动写入 `logs/streamlit.log`，并自动打开 `http://localhost:8501`
- 停止脚本只关闭 `8501` 端口对应 PID，不批量结束 `python.exe`
- 新增 `启动说明.txt`

## V0.6.2

- 项目画像最小可用版：收敛为基础信息、商店图文预览、发行判断卡和短 Markdown 报告。
- 删除/隐藏冗余模板分析，竞品候选不再在画像页默认显示。
- 新增 Steam 评测摘要与评测样本平均/中位游玩时间，失败时显示暂无评测数据。
- Markdown 报告压缩为可直接粘贴的项目画像草稿。

## V0.6.2b

- 发行判断卡改为项目初筛卡。
- 增加数据充分性分级：high / medium / low。
- 数据不足时不再输出假判断或空评测指标。
- Markdown 报告同步压缩为快速初筛口径。

## V0.6.3

- 修复首页卡片未使用 appdetails 补全字段的问题。
- 修复刷新当前卡片详情后卡片字段未同步的问题。
- 首页栏目改为即将推出 / 近期上架 / 热销参考 / 手动观察。
- 来源筛选显示当前实际卡片数量，并增加卡片数据来源调试字段。

## V0.6.4

- 首页新增 Steam 快速搜索。
- 支持游戏名 / AppID / Steam 链接 / SteamDB 链接。
- 搜索结果以图文卡展示，并支持已发售 / 未发售筛选。
- 搜索结果可发送到项目画像和搜索中心。

## V0.6.4a

- 首页新增 Steam 直查入口。
- 支持 AppID / Steam 链接 / SteamDB 链接。
- 直查结果生成单张图文卡。
- 支持发送到一键项目画像。

## V0.6.5

- 新增外部情报手动记录，保存到 `data/external_intel.csv`。
- 支持 YouTube/B站/X/Bluesky/Reddit/官网/Presskit 等来源。
- 项目画像新增外部声量摘要和外部搜索入口，不自动爬取结果。
- Markdown 报告加入外部声量与资料，Excel 导出新增外部情报 sheet。

## V0.6.6

- 新增外部情报库管理能力。
- 支持外部情报过滤、编辑、删除和疑似重复扫描/清理。
- 当前项目外部声量摘要优化，优先按 AppID 匹配。
- 支持导出当前项目外部情报 CSV。

## V0.6.7

- 稳定性收口与已知 bug 修复。
- 修复首页历史/快照刷新与旧记录显示问题。
- 修复 appdetails 已有字段但卡片显示未获取的问题。
- 统一发送到项目画像字段，增强外部情报读写、去重和匹配稳定性。
- 增加数据健康检查区。

## V0.6.9

- 新增快速收录项目入口。
- 支持粘贴 Steam / SteamDB / 社媒链接 / 备注并解析。
- 可保存为项目记录、外部情报并发送到项目画像。
- 工具定位收口为外部发现后的记录与画像生成器。

## V0.6.11a

- 修复启动后重复打开浏览器标签页，后台 Streamlit 改为 headless，由启动器打开一次页面。
- 开发商本体调查表单压缩为摘要、常用字段和更多字段。
- 第三方市场数据录入表单压缩，并明确当前为手动记录卡，不自动抓取。
- 修复 VGI / Gamalytic 错误搜索链接，改为稳定首页入口和复制搜索词。
V0.6.11a-hotfix：修复启动工具只打开浏览器但未启动 Streamlit 服务的问题。
启动流程恢复为先启动服务、等待 localhost:8501 可访问、再由 VBS 只打开一次浏览器。
保留 调试启动.bat 用于可见窗口启动并查看错误。

## V0.6.11a-launch-cleanup

- 弃用 VBS 隐藏启动。
- 启动入口收敛为 启动工具.bat / 停止工具.bat / 运行本地验收.bat / 调试启动.bat。
- 修复启动项过多和 VBS 字符串错误导致的启动失败。

## V0.6.11a

- 压缩开发商本体调查表单。
- 压缩第三方市场数据录入表单。
- 修复 VGI / Gamalytic 错误入口。
- 明确第三方市场数据当前为手动记录模式。

## V0.6.11c

- 首页主入口从“快速收录项目”调整为“查查 / Steam 项目直查”，今日新游雷达移动到查查下方。
- 新增查查搜索历史缓存，支持按游戏名 / AppID / 开发商 / 发行商过滤历史。
- 历史项目记录增加发送到查查、发送到项目画像、打开 Steam / SteamDB 等快捷操作。
- 增加 Steam appdetails 多地区 fallback 和商店页 HTML fallback，修复受地区限制页面导致基础信息断裂的问题。
- 项目画像基础信息下方直接显示商店图文预览。
## V0.6.11c-hotfix

- 修复查查普通文本搜索低相关候选误导问题，候选增加相关性评分和图文预览。
- 低相关候选默认折叠，找不到高相关结果时提示使用 Steam 链接或 AppID。

## V0.6.12

- 新增 Steam 动态 / 公告面板，支持按 AppID 获取最近公告、更新记录、活动新闻。
- 增加 Steam News 本地缓存，项目画像 Markdown 导出加入 Steam 动态章节。

## V0.6.12-hotfix

- 修复 Steam 动态 Markdown 导出参数不匹配报错。
- 增加 Steam 动态内容清洗，去除 HTML/BBCode/转义噪声，并提示接口摘要语言可能不同于当前 Steam 页面语言。

V0.6.12-hotfix2：修复 Markdown 图像报告导出时 steam_news_result 参数不兼容导致的 TypeError。

## V0.6.13

- 新增 Steam 评论预览模块，支持最近评论、有价值评论、最近差评少量展示。
- Markdown 图像报告加入评论预览章节；评论预览仅用于快速判断，不替代完整评论分析器。
