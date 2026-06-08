# MIGRATION_GUIDE

## 换设备继续开发

1. 新电脑安装 Python 3.10+。
2. 复制整个项目文件夹到新电脑，例如：`F:\ai\steam_project_assistant`
3. 进入项目根目录。
4. 双击 `启动_项目初筛助手.bat` 或 `启动_最小化.bat`。
5. 如果依赖缺失，bat 会执行：

```bat
py -3 -m pip install -r requirements.txt
```

6. 如果网页没打开，手动访问：

```text
http://localhost:8501
```

7. 如果端口被占用，先运行：

```bat
停止_项目初筛助手.bat
```

8. 如果需要带走历史数据，必须复制 `data/` 文件夹。
9. 如果只想带走代码，不带工作数据，可以不复制 `data/` 或清空 CSV。
10. 注意：不要把公司敏感资料、公司 Excel 模板、旧公司资料放进公开仓库或个人同步盘。
