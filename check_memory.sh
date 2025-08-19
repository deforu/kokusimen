#!/bin/bash
# メモリ監視ツール実行スクリプト

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "メモリ監視ツールを起動中..."

# 仮想環境をアクティベート
if [ -d "whisper_env" ]; then
    source whisper_env/bin/activate
    echo "仮想環境をアクティベートしました"
else
    echo "エラー: 仮想環境が見つかりません"
    exit 1
fi

# psutilがインストールされているかチェック
python3 -c "import psutil" 2>/dev/null || {
    echo "psutilをインストール中..."
    pip install psutil
}

# メモリ監視ツールを実行
if [ -f "src/memory_monitor.py" ]; then
    python3 src/memory_monitor.py
elif [ -f "memory_monitor.py" ]; then
    python3 memory_monitor.py
else
    echo "エラー: memory_monitor.pyが見つかりません"
    exit 1
fi