#!/bin/bash
# Whisper音声認識システム実行スクリプト

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Whisper音声認識システムを起動中..."

# 仮想環境をアクティベート
if [ -d "whisper_env" ]; then
    source whisper_env/bin/activate
    echo "仮想環境をアクティベートしました"
else
    echo "エラー: 仮想環境が見つかりません"
    echo "setup.shを実行してください"
    exit 1
fi

# メインプログラムを実行
if [ -f "src/whisper_voice_recorder.py" ]; then
    python3 src/whisper_voice_recorder.py
elif [ -f "whisper_voice_recorder.py" ]; then
    python3 whisper_voice_recorder.py
else
    echo "エラー: whisper_voice_recorder.pyが見つかりません"
    exit 1
fi