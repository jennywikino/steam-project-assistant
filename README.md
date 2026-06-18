# Steam 项目初筛助手

## 项目定位

Steam 项目初筛助手是一个面向独立游戏发行/运营场景的本地 Steam 项目筛选工作台。它把项目导入、基础字段补全、发行初筛、候选沉淀和 Excel 输出串成一个轻量工作流，适合用于日常项目发现、试玩优先级判断和候选清单整理。

## 解决的问题

- Steam/SteamDB 页面来回切换成本高
- AppID、开发商、发行商、Demo、简中、评论数等字段重复整理
- 候选项目缺少状态沉淀
- 手动 Excel 整理成本高
- 发行初筛经验难以固化

## 核心功能

- 查查：Steam 链接 / AppID / 游戏名快速直查
- Steam 浏览器采集：浏览 Steam 页面后抓当前页 AppID
- Steam 搜索批量导入：Coming Soon / Demo 池保守分页导入
- SteamDB 手动导入：粘贴 SteamDB 榜单 / AppID
- 基础信息补全：开发商、发行商、发售状态、Demo、简中、类型、评论
- 发行判断建议：待试玩、潜力观察、竞品参考、待补资料
- 候选池：状态管理、下一步动作、备注
- Excel 下载：正式候选、工作日报、候选清单

## 使用流程

1. 启动工具
2. 导入项目
3. 补全信息
4. 筛选候选
5. 发送候选池
6. 导出 Excel

## 技术栈

- Python
- Streamlit
- pandas
- Playwright
- Steam appdetails/cache
- CSV/Excel 本地数据流

## 安全与限制

- 不保存公司敏感数据
- 不提交真实候选池数据
- 不自动爬 SteamDB
- Steam 搜索批量导入默认保守限速
- 适合作为本地工作台，不是 SteamDB/VGI 替代品

## 截图

截图待补齐：

- 首页
- Steam 搜索批量导入
- Steam 浏览器采集
- 候选池
- Excel 导出

## 后续计划

- V0.8.1：截图补齐
- V0.8.2：演示数据脱敏
- V0.9：可选部署/打包

## 本地启动

展示或日常使用推荐双击：

```bat
启动工具_无黑窗.vbs
```

保留调试入口：

```bat
启动工具.bat
```

也可以在项目目录运行：

```bat
python -m streamlit run app.py --server.port 8501
```

浏览器访问：

```text
http://localhost:8501
```

停止后台服务：

```bat
停止工具.bat
```
