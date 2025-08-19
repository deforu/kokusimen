#!/bin/bash
# クラッシュ診断ツール実行スクリプト

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔍 Whisperクラッシュ診断ツールを起動中..."

# 仮想環境をアクティベート
if [ -d "whisper_env" ]; then
    source whisper_env/bin/activate
    echo "仮想環境をアクティベートしました"
else
    echo "エラー: 仮想環境が見つかりません"
    echo "まずsetup.shを実行してください"
    exit 1
fi

# 診断ツールを実行
if [ -f "src/crash_diagnosis.py" ]; then
    python3 src/crash_diagnosis.py
elif [ -f "crash_diagnosis.py" ]; then
    python3 crash_diagnosis.py
else
    echo "エラー: crash_diagnosis.pyが見つかりません"
    exit 1
fi