#!/bin/bash
# Raspberry Pi 5 Whisper音声認識システム セットアップスクリプト

echo "==============================================="
echo "Raspberry Pi 5 Whisper音声認識システム セットアップ"
echo "==============================================="

# システムパッケージの更新
echo "システムパッケージを更新中..."
sudo apt update && sudo apt upgrade -y

# 必要なシステムパッケージのインストール
echo "必要なシステムパッケージをインストール中..."
sudo apt install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    portaudio19-dev \
    alsa-utils \
    pulseaudio \
    pulseaudio-utils \
    ffmpeg \
    git

# Python仮想環境の作成
echo "Python仮想環境を作成中..."
python3 -m venv whisper_env
source whisper_env/bin/activate

# Pythonパッケージのアップグレード
echo "Pythonパッケージをアップグレード中..."
pip install --upgrade pip setuptools wheel

# 必要なPythonライブラリのインストール
echo "必要なPythonライブラリをインストール中..."
pip install \
    openai-whisper \
    pyaudio \
    numpy \
    torch \
    torchaudio

# 音声デバイスの確認
echo "音声デバイスを確認中..."
arecord -l

echo ""
echo "==============================================="
echo "セットアップ完了！"
echo "==============================================="
echo ""
echo "使用方法:"
echo "1. 仮想環境をアクティベート:"
echo "   source whisper_env/bin/activate"
echo ""
echo "2. プログラムを実行:"
echo "   python3 whisper_voice_recorder.py"
echo ""
echo "注意事項:"
echo "- マイクが正しく接続されていることを確認してください"
echo "- 初回実行時にWhisperモデル(small)がダウンロードされます"
echo "- ダウンロードには数分かかる場合があります"
echo ""