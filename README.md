# Raspberry Pi 5 Whisper音声認識システム

Raspberry Pi 5で動作するWhisperを使った音声認識システムです。5秒間の音声を録音して自動的に文字起こしを行います。

## 特徴

- **5秒間の自動録音**: ボタンを押すだけで5秒間録音し、自動的に文字起こし
- **日本語対応**: Whisper smallモデルで日本語音声を高精度で認識
- **リアルタイム処理**: Raspberry Pi 5の性能を活かした高速処理
- **連続録音モード**: 連続して音声認識を実行可能
- **音声デバイステスト**: マイクの動作確認機能付き

## 必要な環境

- **ハードウェア**: Raspberry Pi 5 (8GB推奨)
- **OS**: Raspberry Pi OS (64-bit推奨)
- **マイク**: USB接続マイクまたはPi用マイクモジュール
- **ストレージ**: 最低8GB (Whisperモデル保存用)

## セットアップ

### 1. システムの準備

```bash
# リポジトリをクローン
git clone <このリポジトリのURL>
cd kokusimen

# セットアップスクリプトを実行可能にする
chmod +x setup.sh

# セットアップを実行（10-15分程度かかります）
./setup.sh
```

### 2. 仮想環境のアクティベート

```bash
source whisper_env/bin/activate
```

### 3. 音声デバイスの確認

```bash
# 音声デバイステストツールを実行
python3 audio_test.py
```

## 使用方法

### 基本的な使用方法

```bash
# 仮想環境をアクティベート
source whisper_env/bin/activate

# メインプログラムを実行
python3 whisper_voice_recorder.py
```

### プログラムの機能

1. **1回だけ録音・文字起こし**
   - 5秒間録音してその場で文字起こし
   - テスト用途に最適

2. **連続録音モード**
   - 連続して録音と文字起こしを実行
   - Ctrl+Cで終了

3. **音声デバイステスト**
   - マイクの動作確認
   - 音量レベルの確認
   - デバイス一覧の表示

## トラブルシューティング

### 音声が認識されない場合

1. **マイクの接続確認**
   ```bash
   # 音声デバイス一覧を確認
   arecord -l
   ```

2. **音量レベルの確認**
   ```bash
   # 音声テストツールで音量確認
   python3 audio_test.py
   ```

3. **マイクの音量調整**
   ```bash
   # ALSAミキサーで音量調整
   alsamixer
   ```

### メモリ不足の場合

- Raspberry Pi 5の8GBモデルを使用することを推奨
- 他のアプリケーションを終了してメモリを確保

### 処理が重い場合

- Whisperモデルを"base"や"tiny"に変更
- `whisper_voice_recorder.py`の`load_model("small")`を変更

## 設定のカスタマイズ

### 録音時間の変更

`whisper_voice_recorder.py`の`RECORD_SECONDS`を変更:

```python
self.RECORD_SECONDS = 10  # 10秒に変更
```

### Whisperモデルの変更

使用可能なモデル: `tiny`, `base`, `small`, `medium`, `large`

```python
self.model = whisper.load_model("base")  # baseモデルに変更
```

### サンプリングレートの変更

```python
self.RATE = 44100  # 44.1kHzに変更（高音質）
```

## パフォーマンス最適化

### Raspberry Pi 5での推奨設定

1. **GPU メモリ分割**
   ```bash
   sudo raspi-config
   # Advanced Options > Memory Split > 128
   ```

2. **スワップサイズ増加**
   ```bash
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile
   # CONF_SWAPSIZE=2048 に変更
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

3. **CPUガバナーの設定**
   ```bash
   echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
   ```

## 自動起動設定

### systemdサービスとして登録

```bash
# サービスファイルを作成
sudo nano /etc/systemd/system/whisper-recorder.service
```

サービスファイルの内容:
```ini
[Unit]
Description=Whisper Voice Recorder
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/kokusimen
ExecStart=/home/pi/kokusimen/whisper_env/bin/python /home/pi/kokusimen/whisper_voice_recorder.py
Restart=always

[Install]
WantedBy=multi-user.target
```

サービスを有効化:
```bash
sudo systemctl enable whisper-recorder
sudo systemctl start whisper-recorder
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

バグ報告や機能要望は、GitHubのIssueでお知らせください。

## 参考資料

- [OpenAI Whisper](https://github.com/openai/whisper)
- [Raspberry Pi Documentation](https://www.raspberrypi.org/documentation/)
- [PyAudio Documentation](https://people.csail.mit.edu/hubert/pyaudio/)