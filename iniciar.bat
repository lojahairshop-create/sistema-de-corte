@echo off
echo Iniciando o Orçamento Industrial...
echo Aguarde, o navegador abrira automaticamente.

:: Verifica se a biblioteca principal está instalada
pip show streamlit >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando as dependencias necessarias...
    pip install -r requirements.txt
)

:: Executa o aplicativo
streamlit run app.py
pause
