# Steam 项目初筛助手

当前版本：V0.5.1 无窗口启动器与后台服务管理

这是一个本地使用的 Steam 项目初筛工作台，用来辅助独立游戏发行项目筛选。

当前工具不是全自动爬虫，不接入 Steam 评论工具，不自动查竞品，也不处理公司既有 Excel 模板。`data/projects.csv` 是原始数据仓库，人工阅读请优先使用导出的 `reports/excel/项目总表.xlsx`。

V0.31 新增搜索中心，只生成 Steam、Google、YouTube、B站、Reddit、itch.io、IGDB、SteamDB 等平台的搜索入口和人工填写表格，不真实爬取任何平台。
V0.31a 在搜索中心增加浏览器打开搜索链接功能，支持单条快捷打开和勾选后批量打开。
V0.31b 将搜索中心改为平台搜索导航，平台配置移入 `config/search_platforms.json`，并补充贴吧、NGA、TapTap、小黑盒、游侠、游民星空、巴哈姆特、X、Bluesky 等入口。
V0.31c 增加平台区域搜索策略，国内默认百度站内搜索，港澳台和海外默认 Google 或平台原生搜索，并把同平台同关键词合并为一行展示。
V0.31d 增加搜索中心精简/标准/完整模式和推荐优先搜索，默认不再铺开 300+ 条链接。
V0.31e 修复启停体验：启动脚本会先清理旧的 8501 端口服务，停止脚本只关闭 8501 端口上的后台服务。
V0.4 新增“一键项目画像草稿”：输入 Steam 链接或 AppID 后，尝试读取 Steam 商店公开信息，并用规则生成基础信息、卖点、竞争点、中国区机会、风险、下一步建议和人工确认清单。不接入 AI API，不接入 Steam 评论工具，不做复杂爬虫。
V0.5 新增 SteamDB 发现工作台，用于打开常用榜单、保存 SteamDB 筛选模板、记录榜单观察，并快速导入项目画像。
V0.5.1 新增无窗口启动器、后台服务启动脚本、服务状态检查脚本，并把后台日志输出到 `logs/streamlit.log`。

## 如何启动

日常使用：

```bat
启动_无窗口.vbs
```

双击后会隐藏 cmd 窗口启动后台服务，并自动打开：

```text
http://localhost:8501
```

调试使用：

```bat
启动_项目初筛助手.bat
```

保留旧的最小化启动方式：

```bat
启动_最小化.bat
```

后台服务脚本供 VBS 调用：

```bat
启动_后台服务.bat
```

后台服务会在固定端口 `8501` 启动：

```bat
py -3 -m streamlit run app.py --server.port 8501
```

日志输出到：

```text
logs/streamlit.log
```

关闭浏览器标签页不会关闭后台服务。后台服务仍会占用 `8501` 端口；如果下次打不开，先运行：

```bat
停止_项目初筛助手.bat
```

启动脚本会在启动前自动检查并尝试清理旧的 `8501` 端口进程，只处理占用 `8501` 的进程，不会批量关闭所有 Python。

## 如何停止

退出工具：

```bat
停止_项目初筛助手.bat
```

停止脚本只会停止占用 `8501` 端口的进程，不会批量关闭所有 Python。

检查状态：

```bat
查看_服务状态.bat
```

状态检查脚本会显示 `8501` 是否正在运行，以及对应 PID。

## 如何换设备

1. 在新电脑安装 Python 3.10+。
2. 复制整个项目文件夹到新电脑。
3. 日常使用双击 `启动_无窗口.vbs`，调试时双击 `启动_项目初筛助手.bat`。
4. 如果网页没打开，手动访问 `http://localhost:8501`。
5. 如果需要带走历史数据，必须复制 `data/` 文件夹。

更详细步骤见：`docs/MIGRATION_GUIDE.md` 或 `docs/MIGRATION_GUIDE.txt`。

## 文档位置

- `docs/PROJECT_STATUS.md` / `docs/PROJECT_STATUS.txt`
- `docs/NEXT_STEPS.md` / `docs/NEXT_STEPS.txt`
- `docs/MIGRATION_GUIDE.md` / `docs/MIGRATION_GUIDE.txt`
- `docs/TROUBLESHOOTING.md` / `docs/TROUBLESHOOTING.txt`
- `CHANGELOG.md` / `CHANGELOG.txt`

## 当前支持内容

- 快速记录页，支持 30 秒保存一个项目
- 一键项目画像草稿，支持 Steam URL/AppID 输入和 AppID 自动解析
- Steam 商店公开信息提取：开发商、发行商、发售状态、价格、语言、类型、标签、简介、截图/视频数量、Demo 等字段，获取失败时允许人工补充
- 画像规则生成：卖点草稿、竞争点草稿、中国区发行机会、风险提示、下一步建议、人工确认清单
- 画像联动：可保存为项目记录、生成 Markdown/txt 画像报告、发送到搜索中心、发送到竞品候选发现器
- 搜索中心，半自动生成竞品搜索和全平台声量搜索链接
- 搜索中心平台导航：Steam/商业、国内社区、海外社区、港澳台社区、站内搜索兜底
- 搜索中心区域策略：国内优先百度，巴哈姆特等港澳台平台优先 Google，海外平台不默认百度
- 搜索中心合并展示：同一平台同一关键词只显示一行，备用搜索引擎通过开关展开
- 搜索中心降噪展示：摘要优先、推荐优先搜索、精简/标准/完整模式、分区和平台分组
- 搜索中心链接打开：Google、百度、Steam、SteamDB、YouTube、B站、Reddit、itch、IGDB、TapTap、贴吧、NGA、X、Bluesky 等
- 项目基础信息手动录入
- Demo 试玩记录，深度评估字段默认折叠
- 竞品候选发现器
- 竞品对照表
- 历史项目记录查看、筛选、默认折叠、软删除和恢复
- Markdown/txt 初筛报告生成
- 中文可读 Excel 导出

## 数据说明

- `data/projects.csv`：原始项目数据仓库，不建议直接作为人工阅读表。
- `data/competitors.csv`：正式竞品记录。
- `data/competitor_candidates.csv`：竞品候选池，候选不会自动进入正式竞品表。
- `reports/excel/项目总表.xlsx`：人工阅读用 Excel。
- `reports/profile/`：一键项目画像 Markdown/txt 报告。
- `exports/competitor_search_links.csv`：搜索中心导出的竞品搜索链接。
- `exports/platform_presence_search_links.csv`：搜索中心导出的全平台声量搜索链接。
- `exports/search_navigation_links.csv`：搜索中心平台导航导出。
- `exports/search_navigation_recommended.csv`：搜索中心推荐优先搜索导出。

## 环境信息导出

换设备前可以运行：

```bat
导出_环境信息.bat
```

它会生成：

- `docs/environment_freeze.txt`
- `docs/project_tree.txt`

## 安全提醒

不要把公司敏感资料、公司 Excel 模板、旧公司资料放进公开仓库或个人同步盘。

## 后续计划

- V0.41 优化一键项目画像草稿的字段编辑和旧记录更新
- V0.5 接入已有 Steam 评论分析工具
- V0.6 正式评测报告生成
- V1.0 再考虑打包 exe 或便携包
