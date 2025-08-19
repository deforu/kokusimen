#!/usr/bin/env python3
"""
Raspberry Pi 5用Whisper音声認識システム
5秒間録音して文字起こしを行うプログラム
"""

import pyaudio
import wave
import whisper
import threading
import time
import os
import tempfile
from datetime import datetime

class WhisperVoiceRecorder:
    def __init__(self, model_size="base"):
        # 録音設定
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 16000  # Whisperに最適な16kHz
        self.CHUNK = 1024
        self.RECORD_SECONDS = 5
        
        # モデルサイズの設定
        self.model_size = model_size
        
        # Whisperモデルの初期化
        print(f"Whisperモデル({model_size})を読み込み中...")
        try:
            self.model = whisper.load_model(model_size)
            print(f"Whisperモデル({model_size})の読み込み完了")
        except Exception as e:
            print(f"モデル読み込みエラー: {e}")
            print("より軽量なtinyモデルを試します...")
            self.model = whisper.load_model("tiny")
            self.model_size = "tiny"
            print("Whisperモデル(tiny)の読み込み完了")
        
        # PyAudioの初期化
        self.audio = pyaudio.PyAudio()
        
        # 録音状態
        self.is_recording = False
        self.recording_thread = None
        
    def record_audio(self, filename):
        """5秒間音声を録音する"""
        print(f"録音開始... {self.RECORD_SECONDS}秒間録音します")
        
        stream = self.audio.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK
        )
        
        frames = []
        
        # 録音開始時刻を表示
        start_time = datetime.now()
        print(f"録音開始時刻: {start_time.strftime('%H:%M:%S')}")
        
        # 録音中のカウントダウン表示
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = stream.read(self.CHUNK)
            frames.append(data)
            
            # 1秒ごとにカウントダウン表示
            elapsed = (i + 1) * self.CHUNK / self.RATE
            if elapsed % 1.0 < 0.1:  # 約1秒ごと
                remaining = self.RECORD_SECONDS - int(elapsed)
                if remaining > 0:
                    print(f"残り {remaining} 秒...")
        
        print("録音完了")
        stream.stop_stream()
        stream.close()
        
        # WAVファイルとして保存
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
    def transcribe_audio(self, filename):
        """音声ファイルを文字起こしする"""
        print("文字起こし中...")
        
        try:
            # Whisperで文字起こし実行（メモリ使用量を削減）
            result = self.model.transcribe(
                filename,
                language="ja",  # 日本語に設定
                fp16=False,     # Raspberry Piでは16bit浮動小数点を無効化
                verbose=False,  # 詳細ログを無効化してメモリ節約
                temperature=0,  # 温度を0に設定して一貫性を向上
                compression_ratio_threshold=2.4,  # 圧縮比の閾値を設定
                logprob_threshold=-1.0,  # ログ確率の閾値を設定
                no_speech_threshold=0.6,  # 無音判定の閾値を設定
            )
            
            text = result["text"].strip()
            
            if text:
                print(f"\n=== 文字起こし結果 ({self.model_size}モデル) ===")
                print(f"テキスト: {text}")
                print(f"時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 40)
            else:
                print("音声が検出されませんでした")
                
            return text
            
        except Exception as e:
            print(f"文字起こしエラー: {e}")
            print("メモリ不足の可能性があります。より軽量なモデルを試してください。")
            return None
        
    def record_and_transcribe(self):
        """録音と文字起こしを実行"""
        # 一時ファイル作成
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_filename = temp_file.name
        
        try:
            # 録音実行
            self.record_audio(temp_filename)
            
            # 文字起こし実行
            text = self.transcribe_audio(temp_filename)
            
            return text
            
        finally:
            # 一時ファイル削除
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def start_continuous_recording(self):
        """連続録音モードを開始"""
        print("連続録音モードを開始します")
        print("Ctrl+Cで終了します")
        print("-" * 40)
        
        try:
            while True:
                self.record_and_transcribe()
                print("\n次の録音まで2秒待機...")
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n録音を終了します")
        
    def single_recording(self):
        """1回だけ録音と文字起こしを実行"""
        print("1回だけ録音と文字起こしを実行します")
        print("-" * 40)
        
        text = self.record_and_transcribe()
        return text
    
    def __del__(self):
        """リソースのクリーンアップ"""
        if hasattr(self, 'audio'):
            self.audio.terminate()

def main():
    """メイン関数"""
    print("Raspberry Pi 5 Whisper音声認識システム")
    print("=" * 50)
    
    # モデルサイズの選択
    print("\nWhisperモデルサイズを選択してください:")
    print("1. tiny (最軽量、高速、精度低)")
    print("2. base (軽量、普通速度、精度中)")
    print("3. small (中程度、低速、精度高)")
    
    while True:
        model_choice = input("選択 (1-3、Enterでbase): ").strip()
        if model_choice == "1":
            model_size = "tiny"
            break
        elif model_choice == "2" or model_choice == "":
            model_size = "base"
            break
        elif model_choice == "3":
            model_size = "small"
            break
        else:
            print("無効な選択です。1-3で選択してください。")
    
    print(f"\n選択されたモデル: {model_size}")
    
    # 録音デバイスの確認
    audio = pyaudio.PyAudio()
    print(f"利用可能な録音デバイス数: {audio.get_device_count()}")
    
    # デフォルトの入力デバイス情報を表示
    try:
        default_input = audio.get_default_input_device_info()
        print(f"デフォルト入力デバイス: {default_input['name']}")
    except:
        print("デフォルト入力デバイスが見つかりません")
    
    audio.terminate()
    
    # WhisperVoiceRecorderのインスタンス作成
    recorder = WhisperVoiceRecorder(model_size)
    
    while True:
        print("\n選択してください:")
        print("1. 1回だけ録音・文字起こし")
        print("2. 連続録音モード")
        print("3. 終了")
        
        choice = input("選択 (1-3): ").strip()
        
        if choice == "1":
            recorder.single_recording()
        elif choice == "2":
            recorder.start_continuous_recording()
        elif choice == "3":
            print("プログラムを終了します")
            break
        else:
            print("無効な選択です")

if __name__ == "__main__":
    main()