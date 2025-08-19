#!/bin/bash
# Raspberry Pi 5 Whisper音声認識システム セットアップスクリプト

# 色付きメッセージ用の定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ログファイル
LOGFILE="setup.log"

# エラーハンドリング
set -e
trap 'echo -e "${RED}エラーが発生しました。setup.logを確認してください。${NC}"' ERR

# ログ関数
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOGFILE"
}

echo -e "${BLUE}===============================================${NC}"
echo -e "${BLUE}Raspberry Pi 5 Whisper音声認識システム セットアップ${NC}"
echo -e "${BLUE}===============================================${NC}"

# システム情報の確認
echo -e "\n${YELLOW}システム情報を確認中...${NC}"
log "Raspberry Pi情報:"
cat /proc/device-tree/model 2>/dev/null || echo "Raspberry Pi情報を取得できませんでした" | tee -a "$LOGFILE"
log "OS情報: $(lsb_release -d 2>/dev/null | cut -f2 || cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
log "カーネル: $(uname -r)"
log "メモリ: $(free -h | grep Mem | awk '{print $2}')"

# 現在のディレクトリを記録
CURRENT_DIR=$(pwd)
log "セットアップディレクトリ: $CURRENT_DIR"

# 必要な権限の確認
if ! sudo -n true 2>/dev/null; then
    echo -e "${YELLOW}sudo権限が必要です。パスワードの入力が求められる場合があります。${NC}"
fi

# システムパッケージの更新
echo -e "\n${YELLOW}システムパッケージを更新中...${NC}"
log "システムパッケージ更新開始"
sudo apt update -y 2>&1 | tee -a "$LOGFILE"
sudo apt upgrade -y 2>&1 | tee -a "$LOGFILE"
log "システムパッケージ更新完了"

# 必要なシステムパッケージのインストール
echo -e "\n${YELLOW}必要なシステムパッケージをインストール中...${NC}"
log "システムパッケージインストール開始"

PACKAGES=(
    "python3-pip"
    "python3-dev" 
    "python3-venv"
    "python3-setuptools"
    "portaudio19-dev"
    "alsa-utils"
    "pulseaudio"
    "pulseaudio-utils"
    "ffmpeg"
    "git"
    "build-essential"
    "cmake"
    "pkg-config"
    "libasound2-dev"
    "libportaudio2"
    "libportaudiocpp0"
    "curl"
    "wget"
)

for package in "${PACKAGES[@]}"; do
    echo -e "  ${GREEN}→${NC} インストール中: $package"
    sudo apt install -y "$package" 2>&1 | tee -a "$LOGFILE"
done

log "システムパッケージインストール完了"

# Python仮想環境の作成
echo -e "\n${YELLOW}Python仮想環境を作成中...${NC}"
if [ -d "whisper_env" ]; then
    echo -e "${YELLOW}既存の仮想環境が見つかりました。削除して再作成します。${NC}"
    rm -rf whisper_env
fi

log "Python仮想環境作成開始"
python3 -m venv whisper_env 2>&1 | tee -a "$LOGFILE"

# 仮想環境のアクティベート
source whisper_env/bin/activate
log "仮想環境アクティベート完了"

# Pythonパッケージのアップグレード
echo -e "\n${YELLOW}Pythonパッケージをアップグレード中...${NC}"
log "pipアップグレード開始"
pip install --upgrade pip setuptools wheel 2>&1 | tee -a "$LOGFILE"

# 必要なPythonライブラリのインストール
echo -e "\n${YELLOW}必要なPythonライブラリをインストール中...${NC}"
echo -e "${BLUE}この処理には5-10分程度かかる場合があります...${NC}"

log "Pythonライブラリインストール開始"

# PyTorchを先にインストール（ARM64対応版）
echo -e "  ${GREEN}→${NC} PyTorchをインストール中..."
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu 2>&1 | tee -a "$LOGFILE"

# その他の必要なライブラリ
echo -e "  ${GREEN}→${NC} その他のライブラリをインストール中..."
pip install \
    openai-whisper \
    pyaudio \
    numpy \
    scipy \
    librosa 2>&1 | tee -a "$LOGFILE"

log "Pythonライブラリインストール完了"

# 音声システムの設定
echo -e "\n${YELLOW}音声システムを設定中...${NC}"
log "音声システム設定開始"

# ユーザーをaudioグループに追加
sudo usermod -a -G audio $USER
log "ユーザーをaudioグループに追加"

# PulseAudioの設定
echo -e "  ${GREEN}→${NC} PulseAudioを設定中..."
if ! pgrep -x "pulseaudio" > /dev/null; then
    pulseaudio --start 2>&1 | tee -a "$LOGFILE"
fi

# 音声デバイスの確認
echo -e "\n${YELLOW}音声デバイスを確認中...${NC}"
log "音声デバイス確認:"
arecord -l 2>&1 | tee -a "$LOGFILE"

# Whisperモデルの事前ダウンロード（オプション）
echo -e "\n${YELLOW}Whisperモデルを事前ダウンロードしますか？ (推奨) [y/N]:${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo -e "${YELLOW}Whisperモデル(small)をダウンロード中...${NC}"
    echo -e "${BLUE}この処理には数分かかります...${NC}"
    
    log "Whisperモデルダウンロード開始"
    python3 -c "import whisper; whisper.load_model('small')" 2>&1 | tee -a "$LOGFILE"
    log "Whisperモデルダウンロード完了"
else
    echo -e "${YELLOW}モデルは初回実行時にダウンロードされます。${NC}"
fi

# 実行スクリプトの作成
echo -e "\n${YELLOW}実行スクリプトを作成中...${NC}"
cat > run_whisper.sh << 'EOF'
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
EOF

chmod +x run_whisper.sh
log "実行スクリプト作成完了"

# 音声テストスクリプトの作成
cat > test_audio.sh << 'EOF'
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
EOF

chmod +x test_audio.sh
log "音声テストスクリプト作成完了"

# デスクトップショートカットの作成（デスクトップ環境がある場合）
if [ -n "$DISPLAY" ] && [ -d "$HOME/Desktop" ]; then
    echo -e "\n${YELLOW}デスクトップショートカットを作成中...${NC}"
    
    cat > "$HOME/Desktop/Whisper音声認識.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=Whisper音声認識
Comment=Whisper音声認識システム
Exec=$CURRENT_DIR/run_whisper.sh
Icon=audio-input-microphone
Terminal=true
Categories=AudioVideo;Audio;
StartupNotify=true
EOF
    
    chmod +x "$HOME/Desktop/Whisper音声認識.desktop"
    log "デスクトップショートカット作成完了"
fi

# セットアップ完了
echo -e "\n${GREEN}===============================================${NC}"
echo -e "${GREEN}セットアップ完了！${NC}"
echo -e "${GREEN}===============================================${NC}"
echo ""
echo -e "${BLUE}使用方法:${NC}"
echo -e "${GREEN}1. 簡単起動（推奨）:${NC}"
echo -e "   ${YELLOW}./run_whisper.sh${NC}"
echo ""
echo -e "${GREEN}2. 音声テスト:${NC}"
echo -e "   ${YELLOW}./test_audio.sh${NC}"
echo ""
echo -e "${GREEN}3. 手動起動:${NC}"
echo -e "   ${YELLOW}source whisper_env/bin/activate${NC}"
echo -e "   ${YELLOW}python3 src/whisper_voice_recorder.py${NC}"
echo ""
echo -e "${BLUE}注意事項:${NC}"
echo -e "- マイクが正しく接続されていることを確認してください"
echo -e "- 初回実行時にWhisperモデルがダウンロードされる場合があります"
echo -e "- 詳細なログは ${YELLOW}setup.log${NC} を確認してください"
echo ""
echo -e "${GREEN}システムを再起動することを推奨します${NC}"
echo ""

log "セットアップ完了"