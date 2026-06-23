# CHANGELOG

## V0.9.1-P3d-root-entry-naming-hotfix

- Renamed root user entry files with clear numeric Chinese names.
- Replaced ambiguous dependency and collector setup names with first-time and optional labels.
- Removed duplicate old root entry names.
- Updated startup documentation to point users to the 0 / 1 / 2 / 3 entry flow.

## V0.9.1-P3c-root-entry-cleanup

- Removed duplicate numbered launcher scripts from repository root.
- Removed `START_HERE` folder.
- Removed the VBS launcher from ordinary user entrypoints.
- Moved debug, stop, and local validation scripts away from the root into developer tools.
- Kept only three user-facing Chinese batch files in root.
- Updated startup documentation to clarify first-time and daily usage.

## V0.9.1-P3-release-entrypoint-cleanup

- Added numbered ASCII startup scripts for external users.
- Added `START_HERE` folder with first-time setup entrypoints.
- Fixed and downgraded the VBS launcher that looked for `????.bat`.
- Updated setup documentation to make the first-time flow clearer.
- Kept core app logic unchanged.

## V0.9.1-P2-release-script-encoding-hotfix

- Rewrote Windows batch scripts with ASCII-only content.
- Fixed garbled Chinese output and broken command parsing in CMD.
- Updated Playwright setup script to avoid `.venv` and hard-coded paths.
- Added logs for dependency and Playwright setup.
- Updated external setup documentation.

## V0.9.1-install-feed-source-fix

- 首页项目发现 Feed 默认不再合并 `appdetails cache`，避免“查查 / 项目画像 / 补资料”产生的大游戏缓存污染发现流。
- 首页 Feed 默认来源明确为 Steam 页面采集、候选池 / 导入候选记录、手动观察和 Steam 图文源。
- “刷新首页”改为“重新读取本地数据”，并说明该操作不等于重新抓取 Steam 最新项目。
- 首页高级刷新中保留“强制刷新 Steam 图文源”，并新增首页图文源缓存、appdetails 缓存参考和首页展示状态的清理入口。
- Steam 页面采集环境自动安装增加预计耗时、执行命令、阶段状态和完整输出。
- `安装采集环境.bat` 不再依赖 `.venv`，优先使用 `py -3`，回退 `python`，并写入 `logs/install_playwright.log`。
- README / SETUP 补充 Playwright / Chromium 安装耗时、首页 Feed 本地数据差异和刷新语义说明。

## V0.9.0-portfolio-package

- 保留首页工作台结构和项目发现 Feed。
- 更新 README 为作品集展示版。
- 新增 `docs/portfolio/` 截图目录说明和统一截图命名。
- 补充文档与状态页中的作品集说明。
- 明确核心工作流：项目发现 Feed → 项目导入 → 候选池 → 项目画像 → 导出。
- 未改动候选池、导入和一键画像核心逻辑。

## V0.8.5-P8-history-export-cleanup

- 移除“历史与导出”顶部独立入口。
- 将历史项目记录合并到“一键项目画像”底部，改为“已保存项目画像”折叠区。
- 将删除 / 恢复功能降级为“数据管理 / 恢复记录”折叠区。
- 将项目画像历史导出移动到“一键项目画像”内部。
- 候选池导出继续保留在“竞品与候选”页面。

## V0.8.5-P7-2

- 一键项目画像页调整展示顺序：项目初筛卡后紧跟基础信息 / 商店图文。
- Steam 评论和公告改为基础信息之后的折叠辅助信息。
- 修正最近评论、高赞 / 高价值评论、差评样本共用同一批样本的问题。
- 评论缓存按 appid + language + review_bucket 区分。
- 高价值评论优先按 Steam 返回的有用度字段排序，缺字段时显示人工复核提示。

## V0.8.5-P7-2

- 一键项目画像页调整信息顺序，项目初筛卡前置。
- Steam 公告与评论预览默认折叠，作为辅助证据展示。
- 评论接口失败时不再暴露 SSL 原始错误到主界面。
- 评论正文缺失时继续展示评分与评论数。
- 修正“暂无中文评论样本”的误导性文案。
- 当前项目、公告、评论、初筛卡状态写入 session_state，减少 rerun 丢失。

## V0.8.5-P7-1

- 收敛一键项目画像页主流程。
- 删除或隐藏外部标题线索、公司档案、第三方市场数据、外部声量等低频手填区。
- Steam 公告优先显示中文，中文缺失时 fallback 英文。
- 评论预览改为最近评论 / 高赞评论 / 差评样本分组显示。
- 精简项目初筛卡，删除未接 AI 前不稳定的机会、风险、下一步判断。
- 报告生成改为浏览器下载。
- 候选池操作与候选池页面保持一致。
- 删除竞品候选发现器入口。

## V0.8.5-P6-7-hotfix

- 精简候选池导出结果区域。
- 普通模式仅保留“下载已选候选 CSV / Excel”。
- 移除普通模式下的当前筛选全部导出、完整字段导出、旧版导出入口。
- 调试/兼容导出仅在 debug 模式下保留。

## V0.8.5-P6-6-hotfix

- 修复候选池导出已选项目时错误导出当前筛选全部结果的问题。
- 新增“下载已选候选 CSV / Excel”，默认只导出勾选项目。
- “下载当前筛选全部结果”移入折叠区并明确提示不受勾选影响。
- 精简默认导出字段，完整字段放入调试导出。
- 将处理动作区域收进“处理选中项目”折叠区，优化页面主流程。

## V0.8.5-P6-5-hotfix

- 候选池补资料支持 10 / 30 / 50 / 全部当前筛选。
- 候选池补资料改为未处理缺资料队列，不再重复处理同一批项目。
- 增加“只显示缺资料项目”和“只显示本轮未处理缺资料项目”。
- 增加重置本轮补资料记录。
- 优化搜索建议默认文案，移除“不使用建议”。
- 顶部导航顺序调整为：项目画像在候选池之前。

## V0.8.5-P6-4-hotfix

- 修复候选池开发商 / 发行商搜索不生效。
- 增加开发商 / 发行商候选建议。
- 补资料区明确显示本次处理上限和剩余可补数量。
- 增加本次补全数量选择：10 / 30 / 50 / 全部当前筛选。
- 修复补资料重复处理前 10 条的问题。
- 修复处理台快照不刷新问题。
- 优化资料状态判断。

## V0.8.5-P6-3

- 最近入池改为默认收起，减少第一屏干扰。
- 增加候选池内游戏、开发商、发行商联想搜索。
- 压缩 stage 为 7 个核心处理阶段。
- 增加资料状态与可补资料项目提示。
- 补资料前增加 Steam 访问失败提示。
- 项目处理台改为快速处理下拉 + 手动编辑联动。
- “规则建议”改名为“本地建议”并默认收起。
- 批量处理区去除重复按钮。
- 导出区精简为 CSV / Excel 两个用户版下载按钮。

## V0.8.5-P6-2

- 重整候选池“选中项目处理台”，并使其紧跟主表显示。
- 增加待试玩、值得联系、暂缓、放弃、待补资料等单项目快捷状态流转。
- 增加带确认步骤的已选候选批量字段更新、快捷状态流转和批量归档。
- “应用自动建议”降级为“采用规则建议”，明确其仅来自本地规则。
- 候选池主表改为统一 AppID 选择集合，支持全选当前筛选、反选和清空选择。
- 新增当前筛选候选 CSV / Excel 浏览器下载，使用中文业务表头并隐藏内部字段。
- 旧版落盘导出统一移入默认收起的兼容区域。
- 保存与批量处理反馈移动到对应处理区域，显示成功、失败和更新时间。

## V0.8.5-P6-1

- 候选池新增“最近入池”区域，可查看最近批次的入池时间、来源、数量和示例项目。
- 候选池 schema 补齐 imported_at、source_page、batch_id、import_method 等来源追踪字段。
- 新导入记录保留上游来源和批次；旧记录缺失来源时安全显示未知来源。
- 修复候选池批量补全未稳定请求及写回的问题，基础信息与评测字段只补空值。
- 补全结果显示成功、缓存命中、失败和无 AppID 跳过数量，失败项默认折叠。
- 候选池第一屏重排为候选总览、最近入池、搜索筛选、批量补全和主表。
- 默认主表精简为入池时间、来源、项目基础信息、处理状态及 Steam / 项目画像入口。

## V0.8.5-P5-hotfix2

- 修复 SteamDB 粘贴导入对英文/中文逗号、英文/中文分号和 Tab 分隔内容的解析。
- 纯 AppID 列表可使用空格分隔，普通游戏名文本不会按空格拆分或进入可入池结果。
- 候选池发送反馈移动到发送操作栏下方、当前项目快照之前。
- 用户版 CSV 改为中文表头，并排除无法解析项和内部调试字段。
- 普通导出区域改名为“导出结果”，调试写文件仅在调试模式显示。
- 当前项目快照不再展示解析备注或原始来源工程字段。

## V0.8.5-P5-hotfix

- SteamDB 粘贴导入页收口为文本解析备用入口，明确不支持游戏名搜索。
- 无 AppID 记录不再进入主表、选择集合、项目快照或候选池发送。
- 无法解析记录移入默认收起的独立诊断区。
- 主表删除 Followers、Reviews、Peak 和解析备注等弱字段。
- 当前项目快照默认只显示业务判断字段，SteamDB 指标和解析信息移入折叠区。
- 候选池发送结果统一显示处理统计、明细和候选池状态。
- CSV 导出改为浏览器下载，普通模式不再默认写入 exports。
- 普通模式隐藏榜单观察记录。

## V0.8.5-P5-pre

- SteamDB 粘贴导入页定位为文本解析入口，明确不支持按游戏名搜索或自动抓取 SteamDB。
- 主流程调整为解析内容、补全基础信息、表格选择和发送候选池。
- 普通模式删除“全选高可信”，“全选 AppID”改为“全选可入池项目”。
- 导出解析结果 CSV 移入默认收起的“导出 / 调试”区域。
- 统计统一为当前解析、可入池和已选择。
- 表格、AppID 选择集合、当前项目快照和发送结果对齐另外两个导入页面。

## V0.8.5-P4

- 优化 Steam 页面采集说明，明确工具专用浏览器和推荐抓取页面类型。
- Steam 页面采集定位为列表页采集工具；单个游戏统一提示复制 URL 或游戏名到项目画像。
- 删除“保存本次采集”和“抓取当前游戏”等冗余入口，抓取成功后自动进入本次采集表。
- 移除主界面手动去重；采集结果按 AppID 自动合并或更新。
- 清空本次采集移入默认收起的“危险操作 / 清理数据”。
- 页面采集表格、快速筛选、批量选择、统计和项目快照对齐 Steam 搜索导入交互。
- 统计收口为本次采集、当前筛选、已选择。
- 页面未识别到游戏列表时显示具体处理建议，不 fallback 或修改当前结果。

## V0.8.5-P3-hotfix

- 修复 Playwright 安装后 Steam 页面采集仍提示缺少环境的问题。
- 环境检测改为基于当前 Streamlit 进程的 `sys.executable`。
- 检测 Playwright 包与版本，并实际无头启动 Chromium 验证可用性。
- 缺环境页面新增当前 Python、Playwright 版本、Chromium 启动结果和错误诊断。
- 自动安装改用当前 Python，安装结束后立即重新检测。

## V0.8.5-P3

- 优化 Steam 页面采集缺少 Playwright / Chromium 时的用户提示。
- 新增“自动安装采集环境”按钮，使用项目 `.venv` 安装 Playwright 和 Chromium。
- 新增根目录“安装采集环境.bat”修复工具。
- 明确后续 exe / 应用程序包需要处理 Playwright Chromium 浏览器环境。

## V0.8.5-P2-hotfix-3

- 删除 Steam 搜索导入页当前项目快照中的好评率、评论数和评价字段。
- 搜索导入页只保留批量初筛所需字段，评测详情后移到候选池或项目画像。

## V0.8.5-P2-hotfix-2

- 删除主表“首次发现”，避免误认为 Steam 真实上架时间。
- 工具抓取 / 导入时间仅保留在当前项目快照，并改名为“工具发现时间”。
- 删除主表“好评率”，评测数据后移到候选池和项目画像。
- 主表进一步收口为 13 个字段，保持一屏可读。
- 明确复杂 Steam 筛选应先在 Steam 搜索页完成，再复制 `/search/` URL 导入。
- 保留工具内试玩、发行、自发行、中文、非游戏内容和处理状态筛选。

## V0.8.5-P2-hotfix

- Steam 搜索导入严格限制为标准 `store.steampowered.com/search/` 搜索结果页。
- 新品节活动页、Explore/New、App、Bundle、Sub、开发商页和非 Steam 域名不再 fallback 到默认搜索。
- 不支持 URL 只显示建议，不调用抓取、不清空也不写入当前结果。
- offset、每批数量、请求间隔和最大抓取数量收进默认折叠的高级设置。
- 批次文案统一为当前批次 / 下一批，普通用户无需理解 offset。
- 首次发现日期改为 `yyyy.mm.dd`，快照保留完整时间。
- 主表删除内容 Unknown 列，收口为 15 个主要字段。
- 试玩、中文和好评率显示语义收口；缺失好评率显示 `—`。
- 主表继续不显示查查，仅保留 Steam 和项目画像入口。

## V0.8.5-P2

- Steam 搜索导入表字段语义化，保持 16 列紧凑主表。
- 将 Demo 拆成“内容”和“试玩”，区分游戏、Demo、DLC、Tool、OST 等内容类型。
- 将“简中”改为“中文”，简中或繁中均计为支持中文。
- 时间列压缩为“首次发现”，主表仅显示月日，完整时间保留在快照。
- 删除主表查查入口，保留项目画像作为深入入口。
- 筛选区改为 Steam 源端筛选与本地结果筛选两层结构。
- 增加 offset、当前批次和“抓取下一批”工作流。
- 复用 action log 与候选池数据增加隐藏已处理项目筛选。
- 当前快照复用现有缓存评测接口进行单项目轻量 fallback。
- 查查页重复的项目画像按钮合并为一个“项目画像”。
- 全局观察板 / 可伸缩浮窗延期到 P3，本轮不实现。

## V0.8.5-P1

- 重整项目导入页 Steam 搜索导入 UI。
- 增加导入来源预浏览入口和操作流程说明。
- 把“抓取 AppID”改为“抓取游戏”。
- 增加 Steam 搜索排序依据与高级筛选器；未接入项明确禁用。
- 精简数据管理与快速筛选。
- 重排导入表字段，增加序号、头图、商店上架/首次发现时间。
- 当前项目快照支持在已选项目中切换。
- 删除未接 AI 前价值较低的导入建议、建议理由、下一步动作展示。
- 修复已选数量显示与查看已选项目预览消失问题。

## V0.8.4

- 项目导入页增加选择状态说明，明确当前筛选数量、已选择数量和发送去向。
- Steam 搜索导入、Steam 页面采集、SteamDB 粘贴导入在表格上下增加主动作栏。
- 新增已选项目预览和当前项目标准信息快照。
- 发送候选池后显示本次发送结果面板和发送明细，支持跳转候选池查看。
- 普通模式隐藏完整导入表 / 调试数据。
- 保持 V0.8 功能冻结，不新增抓取能力。

## V0.8.3

- 合并 Steam 浏览器采集、Steam 搜索批量导入、SteamDB 导入为统一“项目导入”页。
- 项目导入页内部按来源切换：Steam 搜索导入 / Steam 页面采集 / SteamDB 粘贴导入。
- 顶部导航进一步精简，突出首页、查查、项目导入、候选池、项目画像。
- 不新增抓取能力，不改现有导入逻辑。

## V0.8.2.2

- 查查页隐藏空缓存模块，简介、截图、评论和公告无内容时不再显示内部缓存提示。
- 查查页调试信息默认隐藏，仅开发调试模式显示原始字段和 JSON。

## V0.8.1

- 首页改为“今日发行筛选工作台”，首屏精简为薄头部、指标、快捷入口、项目发现 Feed、最近操作和低频折叠入口。
- 移除首页首屏能力宣传卡片，改入默认折叠的“关于本工具”。
- 统一首页主刷新入口，高级刷新和缓存维护默认折叠。
- 删除/折叠旧版雷达、常用工具、快照、手动观察和调试 JSON 等低频内容，不再默认执行重逻辑。
- 项目卡片收口为打开 Steam、加入候选池、项目画像、忽略四个动作。
- 加入候选池、发送项目画像、忽略增加 toast、卡片状态和后续入口反馈。
- 新增 `data/action_log.csv` 轻量操作记录，首页默认展示最近 5 条。
- V0.8 继续保持功能冻结，不新增抓取能力，不接 AI，不改 Steam 请求逻辑。

## V0.8.0-P1

- 修复 Steam 搜索批量导入清空后 selected 统计报错，空值、缺失值、NaN、False、0、否均安全统计为未选择。
- 表格选择状态改为 session_state AppID 集合，降低全选当前筛选结果时的卡顿。
- Steam 浏览器采集页和 Steam 搜索批量导入页默认限制展示前 100 条，完整表格放入调试折叠区。
- Steam 搜索批量导入新增清空确认、清空备份和按 AppID 去重备份。
- 清空本次采集/导入时同步清空页面选择状态，不影响候选池。
- 侧边栏退出提醒默认折叠，减少展示版首屏干扰。
- 新增 `启动工具_无黑窗.vbs`，作为展示版推荐启动入口。
- V0.8 继续保持功能冻结，不新增抓取能力。

## V0.8.0

- 首页视觉收口，新增作品集 Hero、关键能力卡片和推荐工作流区。
- README 重写为展示版，补充项目定位、解决的问题、核心功能、使用流程、技术栈、安全与限制。
- 新增 `docs/USER_GUIDE.md`，覆盖启动、查查、Steam 浏览器采集、Steam 搜索批量导入、SteamDB 手动导入、基础信息补全、候选池和 Excel 导出。
- 新增 `docs/PORTFOLIO_NOTE.md`，用于简历/面试场景说明项目背景、业务价值、技术实现和边界。
- 新增 Streamlit 轻量主题配置，保持干净、克制的业务工具风格。
- V0.8 进入作品集展示阶段，不新增核心抓取功能，不接 AI，不改 Steam 搜索批量导入请求逻辑。

## V0.7.4.1

- Steam 搜索批量导入最大数量改为 20 / 50 / 100 / 200 / 500。
- 默认最大导入数量改为 50。
- 500 标记为高风险选项。
- 修复最大数量可能超出 1 条的问题。

## V0.7.4

- 查查入口前置，主导航第 2 位统一显示为“查查”。
- 新增 Steam 搜索批量导入。
- 支持 Coming Soon / Demo 池通过 Steam 搜索分页接口批量导入。
- Steam 浏览器采集表和 Steam 搜索导入表支持批量选择。
- Steam 链接列改为可点击的“打开 Steam”。
- 新品节 / 搜索页不再只依赖手动点“显示更多”。
- V0.8.0 后续进入作品集展示与文档收口。

## V0.7.3.3

- 首页 Feed 分类改为真实发行筛选口径。
- 新增最新采集、未上线/TBA、有 Demo/可试玩、无发行/自发行、热门/评论多、潜力观察、竞品参考。
- 每个分类支持独立加载更多。
- 首页卡片增加项目状态标签。
- 保留 Steam 浏览器采集为新项目发现主入口。
- V0.8.0 后续进入作品集展示与文档收口。

## V0.7.3.2

- 下线 SteamDB 新上架监控入口。
- Steam 浏览器采集默认打开 Steam 商店首页。
- 首页改为项目发现 Feed，支持加载更多。
- 首页低频工具收进折叠区。
- 新项目发现主流程改为 Steam 浏览器采集 + SteamDB 手动粘贴导入。

## V0.7.3.1

- 修复 Steam 浏览器采集的 Playwright 跨线程问题。
- 改为外部浏览器 + 临时 CDP 连接采集，避免在 Streamlit session 中保存 Playwright 对象。

## V0.7.3

- 新增 Steam 浏览器采集助手。
- 支持打开受控 Steam 浏览器。
- 支持从当前页面提取 Steam AppID。
- 支持补全基础信息。
- 支持发送到候选池。
- SteamDB Recent Events 因 403 不再作为主入口。
- Coming Soon / TBA 专项池后续再做。

## V0.7.2.1

- Excel 导出改为内存生成 + 页面下载。
- 默认不再向 exports 目录落盘，避免导出文件堆积。
- 下载保存位置由浏览器控制。

## V0.7.2

- Excel 导出后支持页面下载按钮。
- 用户可通过浏览器选择保存位置。
- exports 目录仍保留历史导出文件，后续可人工归档。

## V0.7.1.1

- 收紧正式候选筛选规则。
- 排除成熟大作、已发售老项目和明显竞品参考项目。
- exports 历史文件改为人工归档提醒。

## V0.7.1

- 新增“正式候选” Sheet，用于隔离可真实跟进的发行候选。
- 新增“工作用日报” Sheet，保留适合复制到日报的精简字段。
- 测试 / 竞品 / 放弃 / 暂缓项目不会污染正式候选导出。
- 日期格式统一暂缓到后续小修。

## V0.7.0

- 新增候选池 Excel 多 Sheet 导出，输出到 `exports/candidate_pool_v070_YYYYMMDD_HHMM.xlsx`。
- 新增“今日日报”Sheet，便于直接复制发行初筛摘要。
- 工具从“查询 / 候选池”进入“可交付输出版”。
- 本版暂不做 API / 网站 / AI，不新增外部数据源。

## V0.6.22-P0

- 新增本地发行判断规则库 `modules/publishing_rules.py`。
- 候选池自动建议基于本地字段刷新，并保留人工状态字段。
- 规则建议不自动覆盖 stage / priority / owner_note / reject_reason / is_archived。

## V0.6.21.1

- 修正 SteamDB 导入重复 AppID 合并逻辑：`AppID {appid}` 占位游戏名可被真实 Steam 游戏名补全。
- 保持真实人工填写游戏名和 stage / priority / owner_note / reject_reason 不被覆盖。

## V0.6.21

- 新增 SteamDB 导入页的 AppID 基础信息补全。
- 支持缓存 Steam 基础信息到 `data/cache/steam_appdetails_cache.json`。
- 发送候选池时优先使用补全后的基础字段。
- 补全失败不影响 AppID-only 入池流程。

## V0.6.20

- 项目画像数据概览改为缩框摘要，展开后保留完整字段。
- 新增 SteamDB 导入页面，支持粘贴 SteamDB 榜单 / 链接 / 多行 AppID 并解析。
- 支持解析结果预览、选择、导出 CSV，并发送选中项到候选池。
- 新增 SteamDB 榜单观察记录，保存到 `data/steamdb_watch_notes.csv`。
- 候选池完整字段支持 SteamDB rank / followers / peak / source。

## V0.6.19-data

- 统一项目数据字段与数据状态展示，补充 Steam 基础信息、素材、评论、公告、第三方市场和缓存状态。
- 增加数据完整度与缺失项提示，项目画像新增数据概览条。
- Steam 动态 / 公告改为结构化显示，并按规则标记“重大更新候选”。
- Steam 评论预览改为最近中文评论、高价值评论、差评样本三组。
- Demo / Playtest 状态统一为有 / 无 / 未确认。
- 第三方市场数据手动区按 SteamDB / VGI / Gamalytic 三列整理。
- 项目画像报告和候选日报补充数据状态字段。

## V0.6.18

- 新增“今日工作流”页面，按日常处理路径串联候选池、查查、项目画像和日报导出。
- 今日工作流支持查看候选统计、筛选待处理候选并选择当前处理项目。
- 当前处理项目支持快速更新阶段、优先级、下一步动作、备注和放弃原因。
- 首页“今日候选工作台”增加进入今日工作流入口。

## V0.6.17-lite

- 优化候选池 AppID 占位记录显示，表格中统一显示资料不足和“补项目画像”兜底。
- 查查 / 项目画像成功获取后可手动回写候选池基础信息。
- 候选池保留轻量“补全当前筛选结果”，最多处理 10 条资料不足或 AppID 占位记录。
- 放弃复杂 data_quality 和大型清理面板，避免工具变重。

## V0.6.16

- 新增候选池批量补全，支持按当前筛选、资料不足、新发现和手动选择范围轻量补全 Steam 基础信息。
- 新增候选自动建议与建议理由，基于现有字段辅助初筛，不自动改动用户状态。
- 新增 `reports/excel/daily_candidate_report_YYYYMMDD.xlsx` 今日候选日报导出。
- 首页增加今日候选工作台摘要，支持跳转候选池、定位资料不足和导出日报。
- 候选池操作支持应用建议与待试玩、待开发商调查、值得联系、暂缓、放弃快速流转。

## V0.6.15-hotfix1

- 修复候选池发送到项目画像时修改已实例化 widget key 导致的 StreamlitAPIException。
- 恢复今日新游雷达标题附近的刷新按钮。
- 候选池筛选项按记录数量自适应折叠。
- 批量导入候选时补全 Steam 基础详情。
- 收紧批量导入 AppID 解析规则。

## V0.6.15

- 新增 `data/candidate_pool.csv` 项目候选池数据文件。
- 支持从项目画像、今日新游雷达、SteamDB 发现加入候选。
- 支持候选状态、优先级、下一步动作管理，并保留忽略 / 放弃记录。
- 支持批量导入 AppID / Steam 链接 / SteamDB 链接。
- 支持导出 `reports/excel/candidate_pool_日期.xlsx` 候选池 Excel。

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
- 不自动爬 SteamDB 榜单，不依赖 SteamDB 公开页面以外的接口，不使用 Selenium

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

## V0.6.14a

- 全局页面减负：高频操作默认展开，低频表单和调试信息默认折叠。
- 整理 SteamDB 发现、搜索中心、Demo 试玩、竞品与候选、项目画像和文档状态页的信息层级。
- 项目画像页保留基础信息、商店图文、项目初筛卡默认可见，Steam 动态、评论预览、公司/市场/外部情报改为按需展开。
