@echo off
echo 黒死面 - Voice AI Assistant Setup for Windows
echo.

REM 仮想環境のアクティベート
call .venv\Scripts\activate.bat

REM 環境変数の設定チェック
if "%GEMINI_API_KEY%"=="" (
    echo エラー: GEMINI_API_KEY が設定されていません
    echo.
    echo Google AI Studio から API キーを取得してください:
    echo https://aistudio.google.com/app/apikey
    echo.
    echo 設定方法:
    echo set GEMINI_API_KEY=your_api_key_here
    echo または .env ファイルを作成してください
    pause
    exit /b 1
)

echo 環境設定完了
echo プログラムを起動しています...
echo.

REM 音声出力チェック
echo %* | findstr /C:"--enable-tts" >nul
if not errorlevel 1 (
    echo 🔊 音声出力モードで起動します
    echo Voicevoxが起動していることを確認してください
    echo.
)

REM プログラム実行
python src\main.py %*