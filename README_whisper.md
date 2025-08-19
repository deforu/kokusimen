# Raspberry Pi 5 Whisper音声認識システム

🎤 **Raspberry Pi 5で動作するWhisperを使った音声認識システム**

5秒間の音声を録音して自動的に文字起こしを行う、Raspberry Pi OS最適化済みシステムです。

## ✨ 特徴

- **🎯 5秒間の自動録音**: ワンクリックで5秒間録音し、自動的に文字起こし
- **🇯🇵 日本語完全対応**: Whisper smallモデルで日本語音声を高精度で認識
- **⚡ リアルタイム処理**: Raspberry Pi 5の8GBメモリを活かした高速処理
- **🔄 連続録音モード**: 連続して音声認識を実行可能
- **🔧 音声デバイステスト**: マイクの動作確認とレベル調整機能付き
- **🚀 ワンクリック起動**: 簡単なスクリプトでシステム起動

## 🖥️ 必要な環境

- **ハードウェア**: Raspberry Pi 5 (8GB推奨)
- **OS**: Raspberry Pi OS (64-bit推奨)
- **マイク**: USB接続マイクまたはPi用マイクモジュール
- **ストレージ**: 最低8GB (Whisperモデル保存用)

## 🚀 クイックスタート

### 1. 自動セットアップ（推奨）

```bash
# リポジトリをクローン
git clone https://github.com/deforu/kokusimen.git
cd kokusimen

# ワンコマンドセットアップ（10-15分程度）
chmod +x setup.sh
./setup.sh
```

### 2. 簡単起動

```bash
# メインプログラム起動
./run_whisper.sh

# または音声テスト
./test_audio.sh
```

## 📋 詳細セットアップ

### ステップ1: システム準備

```bash
# システム更新
sudo apt update && sudo apt upgrade -y

# 必要なパッケージ確認
sudo apt install git curl
```

### ステップ2: プロジェクトダウンロード

```bash
# ホームディレクトリに移動
cd ~

# プロジェクトをクローン
git clone https://github.com/deforu/kokusimen.git
cd kokusimen
```

### ステップ3: セットアップ実行

```bash
# セットアップスクリプトを実行可能にする
chmod +x setup.sh

# セットアップ実行（詳細ログ付き）
./setup.sh
```

このスクリプトは以下を自動実行します：

- ✅ 必要なシステムパッケージのインストール
- ✅ Python仮想環境の作成
- ✅ 必要なPythonライブラリのインストール
- ✅ 音声システムの設定
- ✅ Whisperモデルの事前ダウンロード（オプション）
- ✅ 実行スクリプトの作成
- ✅ デスクトップショートカットの作成

### ステップ4: 音声デバイス確認

```bash
# 音声テストツールで確認
./test_audio.sh
```

## 🎯 使用方法

### 基本的な使用方法

1. **簡単起動**（推奨）
   ```bash
   ./run_whisper.sh
   ```

2. **手動起動**
   ```bash
   source whisper_env/bin/activate
   python3 src/whisper_voice_recorder.py
   ```

### プログラムの機能

起動すると以下のメニューが表示されます：

```
選択してください:
1. 1回だけ録音・文字起こし
2. 連続録音モード  
3. 終了
```

#### オプション1: 1回だけ録音・文字起こし
- 5秒間録音してその場で文字起こし
- テスト用途に最適

#### オプション2: 連続録音モード
- 連続して録音と文字起こしを実行
- `Ctrl+C`で終了

## 🔧 トラブルシューティング

### 音声が認識されない場合

1. **マイクの接続確認**
   ```bash
   # 音声デバイス一覧を確認
   arecord -l
   ```

2. **音量レベルの確認**
   ```bash
   # 音声テストツールで音量確認
   ./test_audio.sh
   ```

3. **マイクの音量調整**
   ```bash
   # ALSAミキサーで音量調整
   alsamixer
   ```

### PulseAudioの問題

```bash
# PulseAudioを再起動
pulseaudio --kill
pulseaudio --start

# または
sudo systemctl restart pulseaudio
```

### メモリ不足の場合

```bash
# スワップサイズを増やす
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=2048 に変更
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

### 処理が重い場合

Whisperモデルを軽量版に変更：

```python
# src/whisper_voice_recorder.py の73行目付近
self.model = whisper.load_model("base")  # smallからbaseに変更
# または
self.model = whisper.load_model("tiny")  # より軽量
```

## ⚙️ カスタマイズ

### 録音時間の変更

`src/whisper_voice_recorder.py`の`RECORD_SECONDS`を変更:

```python
self.RECORD_SECONDS = 10  # 10秒に変更
```

### サンプリングレートの変更

```python
self.RATE = 44100  # 44.1kHzに変更（高音質）
```

### Whisperモデルの選択

使用可能なモデル: `tiny`, `base`, `small`, `medium`, `large`

```python
self.model = whisper.load_model("base")  # お好みのモデルに変更
```

## 🚀 パフォーマンス最適化

### Raspberry Pi 5での推奨設定

1. **GPUメモリ分割**
   ```bash
   sudo raspi-config
   # Advanced Options > Memory Split > 128MB
   ```

2. **CPUパフォーマンスモード**
   ```bash
   # 一時的に設定
   echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
   
   # 永続的に設定
   echo 'echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor' | sudo tee -a /etc/rc.local
   ```

## 🏃‍♂️ 自動起動設定

### systemdサービスとして登録

```bash
# サービスファイルをコピー
sudo cp whisper-recorder.service /etc/systemd/system/

# パスを編集（必要に応じて）
sudo nano /etc/systemd/system/whisper-recorder.service

# サービスを有効化
sudo systemctl enable whisper-recorder
sudo systemctl start whisper-recorder

# ステータス確認
sudo systemctl status whisper-recorder
```

## 📁 プロジェクト構造

```
kokusimen/
├── setup.sh                    # 自動セットアップスクリプト
├── run_whisper.sh              # メインプログラム起動スクリプト
├── test_audio.sh               # 音声テストスクリプト
├── requirements.txt            # Python依存関係
├── whisper-recorder.service    # systemdサービスファイル
├── src/
│   ├── whisper_voice_recorder.py  # メインプログラム
│   └── audio_test.py              # 音声テストツール
└── README.md                   # このファイル
```

## 🐛 ログとデバッグ

### セットアップログの確認

```bash
# セットアップ時のログを確認
cat setup.log
```

### 実行時のデバッグ

```bash
# 詳細なデバッグ情報付きで実行
source whisper_env/bin/activate
python3 -v src/whisper_voice_recorder.py
```

## 💡 使用例

### 基本的な流れ

1. `./run_whisper.sh` でプログラム起動
2. メニューで「1」を選択
3. 「録音開始...」のメッセージ後、5秒間話す
4. 文字起こし結果が表示される

### 実行例

```bash
$ ./run_whisper.sh
Whisper音声認識システムを起動中...
仮想環境をアクティベートしました
Raspberry Pi 5 Whisper音声認識システム
==================================================

選択してください:
1. 1回だけ録音・文字起こし
2. 連続録音モード
3. 終了
選択 (1-3): 1

録音開始... 5秒間録音します
録音開始時刻: 14:30:25
残り 4 秒...
残り 3 秒...
残り 2 秒...
残り 1 秒...
録音完了
文字起こし中...

=== 文字起こし結果 ===
テキスト: こんにちは、今日はいい天気ですね。
時刻: 2025-08-20 14:30:30
==============================
```

## 📄 ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 🤝 貢献

バグ報告や機能要望は、GitHubのIssueでお知らせください。

## 📚 参考資料

- [OpenAI Whisper](https://github.com/openai/whisper)
- [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/)
- [PyAudio Documentation](https://people.csail.mit.edu/hubert/pyaudio/)

## 🔖 バージョン履歴

- **v1.0.0** - 初回リリース
  - 5秒録音機能
  - Whisper smallモデル対応
  - 連続録音モード
  - 音声デバイステスト機能