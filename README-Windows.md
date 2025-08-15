# 黒死面 (Windows対応版)

しゃべるのが苦手な人の代わりに、短い発話を丁寧な返答に整えて話してくれる"魔法のマスク"プロジェクト。現在は 音声入力 → テキスト化（Whisper） → AI応答（Gemini）が動作。

## 実装機能
- [x] Whisper + Gemini応答テキスト
- [x] AI応答テキストの音声出力（Voicevox対応）
- [ ] 話者認識（できたらやる）
- [ ] 感情分析（できたらやる）
- [ ] LED制御（できたらやる）

## 概要
- ローカル音声認識: faster-whisper（CTranslate2, CPU/INT8）
- 生成AI応答: Google Gemini（`google-generativeai` SDK）
- 音声合成: Voicevox（ローカル音声合成エンジン）
- Windows/ラズパイで動作を想定。小型モデル＋INT8で軽量化。

## Windows セットアップ手順

### 1. 前提条件
- Windows 10/11
- Python 3.9+（推奨: 3.11以上）
- マイク（内蔵またはUSB）
- スピーカーまたはヘッドホン（音声出力用）
- ネット接続（Gemini利用のため）
- Voicevox（音声出力を使用する場合）

### 2. プロジェクトセットアップ
```powershell
# リポジトリをクローンまたはダウンロード
cd path\to\kokusimen

# 仮想環境作成とアクティベート
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# 依存関係インストール
pip install --upgrade pip
pip install -r requirements.txt
pip install python-dotenv
```

### 3. Voicevox セットアップ（音声出力用、オプション）

音声で応答を聞きたい場合は、Voicevoxをインストール：

1. **Voicevoxのダウンロード**
   - [Voicevox公式サイト](https://voicevox.hiroshiba.jp/) からダウンロード
   - Windows版をインストール

2. **Voicevoxの起動**
   ```
   Voicevoxを起動（通常は http://127.0.0.1:50021 で起動）
   ```

3. **話者確認**
   ```powershell
   python show_speakers.py
   ```

### 4. API キー設定

#### 方法1: 環境変数で設定（推奨）
```powershell
# PowerShell で設定
$env:GEMINI_API_KEY="your_api_key_here"
```

#### 方法2: .env ファイルで設定
```
# .env ファイルを作成（.env.example をコピー）
GEMINI_API_KEY=your_api_key_here
```

### 4. Google Gemini API キーの取得
1. [Google AI Studio](https://aistudio.google.com/app/apikey) にアクセス
2. 「Create API Key」をクリック
3. 生成されたAPIキーをコピー
4. 上記の方法で環境変数に設定

## 使い方

### コマンドライン
```powershell
# テキスト出力のみ（基本使用）
python src\main.py -s 4 --model small --compute int8

# 音声出力付き（Voicevoxが起動している場合）
python src\main.py -s 4 --model small --enable-tts

# カスタム話者で音声出力
python src\main.py -s 6 --model base --enable-tts --speaker-id 3

# 利用可能な話者を確認
python show_speakers.py
```

### バッチファイル（簡単実行）
```cmd
# コマンドプロンプト用
run.bat

# PowerShell用  
.\run.ps1
```

## 主なオプション
- `-s/--seconds`: 1ターンの録音秒数（既定: 8）
- `--model`: faster-whisperモデル（`tiny`, `base`, `small`, `medium`, `large`）
- `--compute`: 計算精度 (`int8`, `int16`, `float32` 等、既定: `int8`)
- `--lang`: 認識言語（既定: `ja`）
- `--enable-tts`: Voicevox音声出力を有効化
- `--speaker-id`: Voicevox話者ID（既定: 1 - 四国めたん）
- `--system`: Geminiへのシステムプロンプト

## マイク動作確認
Windows でマイクの動作を確認：
1. 「設定」→「プライバシーとセキュリティ」→「マイク」
2. アプリがマイクにアクセス可能か確認
3. 音量レベルの調整

## モデル選択の目安
- **速度優先**: `--model tiny --compute int8`（精度は低め）
- **バランス**: `--model small --compute int8`（推奨）
- **精度優先**: `--model base --compute int16`（少し重い）

## トラブルシュート

### 音声認識関連
- **録音できない**: マイクのプライバシー設定、デバイスマネージャーでマイクを確認
- **音声が認識されない**: 録音秒数を長くする、マイク音量を上げる
- **雑音が多い**: 静かな環境で試す、マイクの位置を調整

### 音声出力関連
- **音声が再生されない**: スピーカー/ヘッドホンの接続確認、音量設定
- **Voicevoxエラー**: Voicevoxが起動しているか確認（http://127.0.0.1:50021）
- **音声出力が遅い**: 話者IDを変更、Voicevoxの設定確認

### API関連
- **`GEMINI_API_KEY` 未設定エラー**: 上記のAPI キー設定手順を確認
- **レスポンスが遅い**: モデルを `tiny` に変更、録音秒数を短縮
- **API制限エラー**: しばらく待ってから再試行

### パフォーマンス
- **処理が重い**: `--model tiny --compute int8` を試す
- **メモリ不足**: 他のアプリケーションを終了してメモリを確保

## ファイル構成
```
kokusimen/
├── src/
│   ├── main.py          # メインプログラム
│   ├── audio.py         # 音声録音
│   ├── transcribe.py    # 音声認識（Whisper）
│   ├── llm.py           # AI応答（Gemini）
│   └── tts.py           # 音声合成（Voicevox）
├── requirements.txt     # Python依存関係
├── .env.example        # 環境変数サンプル
├── run.bat             # Windows バッチファイル
├── run.ps1             # PowerShell スクリプト
├── check_setup.py      # 環境チェックスクリプト
├── show_speakers.py    # Voicevox話者確認
└── README.md           # このファイル
```

## 開発・カスタマイズ

### システムプロンプトの変更
`.env` ファイルまたは `--system` オプションでカスタマイズ可能：
```
SYSTEM_PROMPT=あなたは親しみやすいアシスタントです。ユーザーの発話を自然な日本語で丁寧に返答してください。
```

### 他の言語での使用
`--lang` オプションで言語を指定：
```powershell
python src\main.py --lang en --enable-tts  # 英語
python src\main.py --lang zh --enable-tts  # 中国語
```

### 話者の変更
利用可能な話者を確認してから変更：
```powershell
# 話者一覧を表示
python show_speakers.py

# 特定の話者を使用（例: ID 3）
python src\main.py --enable-tts --speaker-id 3
```

---

**注意**: このプロジェクトはオリジナル版（Raspberry Pi向け）をWindows対応させたものです。