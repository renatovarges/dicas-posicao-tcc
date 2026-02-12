@echo off
echo Iniciando o Gerador de Dicas por Posicao...
cd /d "%~dp0"
streamlit run app.py
pause
