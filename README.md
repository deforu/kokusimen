# 黒死面

しゃべるのが苦手な人の代わりに、短い発話を丁寧な返答に整えて話してくれる“魔法のマスク”プロジェクト。現在は 音声入力 → テキスト化（Whisper） → AI応答（Gemini）が動作。周辺機能は順次拡張。

### 実装機能
- [x] Whisper + Gemini 音声アシスタント（Raspberry Pi）
- [ ] AI応答テキストの音声出力
- [ ] 話者認識（できたらやる）
- [ ] 感情分析（できたらやる）
- [ ] LED制御（できたらやる）

概要
- ローカル音声認識: faster-whisper（CTranslate2, CPU/INT8）
- 生成AI応答: Google Gemini（`google-generativeai` SDK）
- ラズパイで動作を想定。小型モデル＋INT8で軽量化。

動作要件（Raspberry Pi OS 64-bit 推奨）
- Raspberry Pi 4/5（64-bit OS 推奨）
- Python 3.9+（推奨: 3.11）
- USBマイクまたはI2Sマイク、スピーカー
- ネット接続（Gemini利用のため）

システムパッケージのインストール
```bash
sudo apt update
sudo apt install -y python3-venv libportaudio2 ffmpeg libopenblas-dev
# （任意、音声応答したい場合）
sudo apt install -y libttspico-utils alsa-utils
```

プロジェクトセットアップ
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Gemini APIキーを設定（シェルに合わせて export/set）
export GEMINI_API_KEY="YOUR_API_KEY"
```

使い方
```bash
# 対話モード（Enterで録音開始→指定秒数で自動終了）
python src/main.py -s 8 --model tiny --compute int8 --say
```

主なオプション
- `-s/--seconds`: 1ターンの録音秒数（既定: 8）
- `--model`: faster-whisperモデル（例: `tiny`, `base`, `small`）。まずは`tiny`推奨
- `--compute`: `int8`/`int16`/`float32` など（既定: `int8`）
- `--lang`: 認識言語（既定: `ja`）
- `--say`: 回答を音声合成（`pico2wave` + `aplay` がある場合）
- `--system`: Geminiへのシステムプロンプト（既定: やさしい日本語アシスタント）

マイク動作確認のヒント
- `arecord -l` でデバイス一覧
- `alsamixer` で入力レベル調整
- 録音が失敗する場合はユーザーを `audio` グループへ: `sudo usermod -a -G audio $USER` → 再起動

モデル選択の目安（Pi）
- 速度優先: `--model tiny --compute int8`
- 精度優先: `--model base` または `small`（遅くなる）

トラブルシュート
- `GEMINI_API_KEY` が未設定: 環境変数を設定してください
- 録音でエラー: `libportaudio2` の導入、サンプリングレート（既定16kHz）を見直す
- 応答が遅い: モデルを `tiny` に、録音秒数を短く

# kokusimen
