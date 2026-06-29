# Steam Project Assistant Agent Rules

## 项目定位

Steam Project Assistant 是面向独立游戏发行选品场景的 Steam 独立游戏项目初筛助手。

核心价值是把 Steam 项目发现、资料补全、候选池筛选、项目画像和导出整理成一套可复用的发行工作流。

## 重要原则

- 不要大改首页结构。
- 首页项目发现 Feed 是核心展示，不要改成纯作品集介绍页。
- 不要重构无关文件。
- 不要覆盖人工字段。
- 不要提交真实 `data/`、`cache/`、`exports/`、`reports/`、`debug/`、`logs/`。
- 不要提交 `dist/`、`dist_test/`、`tools/runtime/`。
- 不要把打包产物提交进 Git。
- 不要把 appdetails cache 默认混入首页 Feed。
- 不要把“重新读取本地数据”写成“联网刷新”。
- Steam 图文源联网刷新必须和本地读取区分。
- 修改前先定位相关函数，少扫全仓库。
- 每次任务只处理 `docs/TASK_HANDOFF.md` 中的问题。
- 改完必须输出修改文件、原因、验收步骤、风险和 `git status`。

## 启动与验证命令

基础编译验证：

```powershell
py -3 -m py_compile app.py
```

如果修改了 `modules/` 文件，额外对对应文件运行：

```powershell
py -3 -m py_compile modules/对应文件.py
```

启动源码版时，优先使用仓库现有启动 `.bat`；也可以运行：

```powershell
python -m streamlit run app.py
```

不能随便运行删除缓存、重置 Git、递归删除目录等破坏性清理命令。

## Codex 档位规则

- 文案、README、bat、路径提示：低。
- 明确 bug 但需要定位文件：中。
- 数据流、缓存、导入导出、候选池：中到高。
- 新模块、大型重构：高。
- 默认不要使用超高档位。
