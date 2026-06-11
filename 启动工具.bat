@echo off
cd /d F:\ai\steam_project_assistant
python -m streamlit run app.py --server.port 8501 --server.headless false
pause
