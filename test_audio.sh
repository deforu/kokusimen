#!/bin/bash
# 音声テスト実行スクリプト

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "音声デバイステストを起動中..."

# 仮想環境をアクティベート
if [ -d "whisper_env" ]; then
    source whisper_env/bin/activate
    echo "仮想環境をアクティベートしました"
else
    echo "エラー: 仮想環境が見つかりません"
    exit 1
fi

# 音声テストプログラムを実行
if [ -f "src/audio_test.py" ]; then
    python3 src/audio_test.py
elif [ -f "audio_test.py" ]; then
    python3 audio_test.py
else
    echo "エラー: audio_test.pyが見つかりません"
    exit 1
fi