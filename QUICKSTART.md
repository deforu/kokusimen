# 🚀 Raspberry Pi 5 クイックスタートガイド

このガイドでは、Raspberry Pi 5でWhisper音声認識システムを最短時間で動かす方法を説明します。

## ⏱️ 所要時間: 約15分

## 📋 準備するもの

- ✅ Raspberry Pi 5 (8GB推奨)
- ✅ Raspberry Pi OS (64-bit) インストール済み
- ✅ USBマイク または Pi用マイクモジュール
- ✅ インターネット接続

## 🎯 ステップバイステップ

### ステップ 1: ターミナルを開く

Raspberry Pi OSのデスクトップで：
- 画面上部のターミナルアイコンをクリック
- または `Ctrl + Alt + T` を押す

### ステップ 2: プロジェクトをダウンロード

```bash
# ホームディレクトリに移動
cd ~

# プロジェクトをダウンロード
git clone https://github.com/deforu/kokusimen.git

# プロジェクトディレクトリに移動
cd kokusimen
```

### ステップ 3: 自動セットアップを実行

```bash
# セットアップスクリプトを実行可能にする
chmod +x setup.sh

# セットアップを開始（10-15分程度かかります）
./setup.sh
```

**⚠️ 重要**: セットアップ中に以下が表示されます：
- `sudo`パスワードの入力要求 → Raspberry Piのパスワードを入力
- Whisperモデルダウンロードの確認 → `y` を入力（推奨）

### ステップ 4: マイクをテスト

```bash
# 音声デバイステストを実行
./test_audio.sh
```

テストメニューで：
1. `1` → 音声デバイス一覧を確認
2. `2` → マイクテスト録音を実行
3. 音量が適切に表示されることを確認

### ステップ 5: メインプログラムを起動

```bash
# Whisper音声認識システムを起動
./run_whisper.sh
```

### ステップ 6: 音声認識を試す

プログラム起動後：
1. メニューで `1` を選択（1回だけ録音・文字起こし）
2. 「録音開始...」と表示されたら、5秒間話す
3. 文字起こし結果が表示される

## 🎉 成功例

正常に動作すると以下のような表示になります：

```
=== 文字起こし結果 ===
テキスト: こんにちは、今日はいい天気ですね。
時刻: 2025-08-20 14:30:30
==============================
```

## 🔧 トラブルが発生した場合

### マイクが認識されない

```bash
# 音声デバイスを確認
arecord -l

# USBマイクの場合は再接続
# 内蔵マイクの場合は音量を確認
alsamixer
```

### セットアップでエラーが出る

```bash
# ログファイルを確認
cat setup.log

# システムを更新してから再実行
sudo apt update && sudo apt upgrade -y
./setup.sh
```

### メモリ不足エラー

```bash
# 利用可能メモリを確認
free -h

# スワップを増やす
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=2048 に変更
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

## 📱 便利な使い方

### デスクトップから起動

セットアップ完了後、デスクトップに「Whisper音声認識」ショートカットが作成されます。
ダブルクリックで起動できます。

### 連続使用モード

```bash
./run_whisper.sh
# メニューで「2」を選択すると連続録音モード
# Ctrl+C で終了
```

### システム起動時に自動起動

```bash
# サービスとして登録
sudo cp whisper-recorder.service /etc/systemd/system/
sudo systemctl enable whisper-recorder
sudo systemctl start whisper-recorder
```

## 🎯 次のステップ

システムが正常に動作したら：

1. **録音時間をカスタマイズ**: `src/whisper_voice_recorder.py` を編集
2. **モデルサイズを調整**: 処理速度 vs 精度のバランスを調整
3. **自動起動を設定**: システム起動時に自動でサービス開始

## 💬 サポート

問題が解決しない場合は：
- 📄 詳細な `README_whisper.md` を確認
- 🐛 GitHubのIssueで報告
- 📋 `setup.log` の内容を添付

---

**🎉 お疲れ様でした！これでRaspberry Pi 5でWhisper音声認識システムが使えるようになりました。**