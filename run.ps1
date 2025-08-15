# PowerShell スクリプト for 黒死面
Write-Host "黒死面 - Voice AI Assistant Setup for Windows" -ForegroundColor Cyan
Write-Host ""

# 仮想環境のアクティベート
& ".\.venv\Scripts\Activate.ps1"

# 環境変数の設定チェック
if (-not $env:GEMINI_API_KEY) {
    Write-Host "エラー: GEMINI_API_KEY が設定されていません" -ForegroundColor Red
    Write-Host ""
    Write-Host "Google AI Studio から API キーを取得してください:" -ForegroundColor Yellow
    Write-Host "https://aistudio.google.com/app/apikey" -ForegroundColor Blue
    Write-Host ""
    Write-Host "設定方法:" -ForegroundColor Yellow
    Write-Host '$env:GEMINI_API_KEY="your_api_key_here"' -ForegroundColor Green
    Write-Host "または .env ファイルを作成してください" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "環境設定完了" -ForegroundColor Green
Write-Host "プログラムを起動しています..." -ForegroundColor Cyan
Write-Host ""

# プログラム実行（音声出力オプション付き）
if ($args -contains "--enable-tts" -or $args -contains "--tts") {
    Write-Host "🔊 音声出力モードで起動します" -ForegroundColor Green
    Write-Host "Voicevoxが起動していることを確認してください" -ForegroundColor Yellow
}

python src\main.py $args