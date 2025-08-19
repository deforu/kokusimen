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
import traceback
import gc
import psutil
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
        
        # 初期メモリ使用量をチェック
        self.log_memory_usage("初期化前")
        
        # Whisperモデルの初期化
        print(f"Whisperモデル({model_size})を読み込み中...")
        try:
            # メモリ不足対策：ガベージコレクション実行
            gc.collect()
            
            self.model = whisper.load_model(model_size, device="cpu")
            self.log_memory_usage(f"モデル({model_size})読み込み後")
            print(f"Whisperモデル({model_size})の読み込み完了")
            
        except Exception as e:
            print(f"モデル読み込みエラー: {e}")
            print(f"エラー詳細: {traceback.format_exc()}")
            
            if model_size != "tiny":
                print("より軽量なtinyモデルを試します...")
                try:
                    gc.collect()  # メモリ解放
                    self.model = whisper.load_model("tiny", device="cpu")
                    self.model_size = "tiny"
                    self.log_memory_usage("tinyモデル読み込み後")
                    print("Whisperモデル(tiny)の読み込み完了")
                except Exception as e2:
                    print(f"tinyモデルの読み込みも失敗: {e2}")
                    print(f"詳細エラー: {traceback.format_exc()}")
                    raise RuntimeError("すべてのWhisperモデルの読み込みに失敗しました")
            else:
                raise e
        
        # PyAudioの初期化
        try:
            self.audio = pyaudio.PyAudio()
            print("PyAudio初期化完了")
        except Exception as e:
            print(f"PyAudio初期化エラー: {e}")
            raise e
        
        # 録音状態
        self.is_recording = False
        self.recording_thread = None
        
        self.log_memory_usage("初期化完了")
    
    def log_memory_usage(self, stage):
        """メモリ使用量をログ出力"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            system_memory = psutil.virtual_memory()
            
            print(f"[{stage}] メモリ使用量:")
            print(f"  プロセス: {memory_info.rss / 1024 / 1024:.1f} MB")
            print(f"  システム: {system_memory.used / 1024 / 1024:.0f} MB / {system_memory.total / 1024 / 1024:.0f} MB ({system_memory.percent:.1f}%)")
            print(f"  利用可能: {system_memory.available / 1024 / 1024:.0f} MB")
        except Exception as e:
            print(f"メモリ情報取得エラー: {e}")
        
    def record_audio(self, filename):
        """5秒間音声を録音する"""
        print(f"録音開始... {self.RECORD_SECONDS}秒間録音します")
        
        stream = None
        wf = None
        
        try:
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
                try:
                    data = stream.read(self.CHUNK, exception_on_overflow=False)
                    frames.append(data)
                    
                    # 1秒ごとにカウントダウン表示
                    elapsed = (i + 1) * self.CHUNK / self.RATE
                    if elapsed % 1.0 < 0.1:  # 約1秒ごと
                        remaining = self.RECORD_SECONDS - int(elapsed)
                        if remaining > 0:
                            print(f"残り {remaining} 秒...")
                            
                except Exception as e:
                    print(f"録音データ読み取りエラー: {e}")
                    break
            
            print("録音完了")
            
            if stream:
                stream.stop_stream()
                stream.close()
            
            if not frames:
                print("❌ 録音データが取得できませんでした")
                return
            
            # WAVファイルとして保存
            try:
                wf = wave.open(filename, 'wb')
                wf.setnchannels(self.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(self.FORMAT))
                wf.setframerate(self.RATE)
                wf.writeframes(b''.join(frames))
                wf.close()
                
                # ファイル保存確認
                if os.path.exists(filename) and os.path.getsize(filename) > 0:
                    print(f"✅ 録音ファイル保存完了: {filename}")
                else:
                    print("❌ 録音ファイルの保存に失敗しました")
                    
            except Exception as e:
                print(f"❌ WAVファイル保存エラー: {e}")
                if wf:
                    wf.close()
                raise e
                
        except Exception as e:
            print(f"❌ 録音エラー: {e}")
            print(f"エラータイプ: {type(e).__name__}")
            
            if "Input overflowed" in str(e):
                print("💡 入力オーバーフロー: マイクの音量を下げてください")
            elif "Device unavailable" in str(e):
                print("💡 デバイス利用不可: マイクの接続を確認してください")
            
            raise e
            
        finally:
            if stream:
                try:
                    stream.stop_stream()
                    stream.close()
                except:
                    pass
        
    def transcribe_audio(self, filename):
        """音声ファイルを文字起こしする"""
        print("文字起こし中...")
        
        # 文字起こし前のメモリ状況をチェック
        try:
            memory = psutil.virtual_memory()
            available_mb = memory.available // (1024 * 1024)
            print(f"文字起こし開始前の利用可能メモリ: {available_mb} MB")
            
            if available_mb < 300:  # 300MB未満の場合は警告
                print("⚠️ 利用可能メモリが不足しています。ガベージコレクションを実行...")
                gc.collect()
                memory = psutil.virtual_memory()
                available_mb = memory.available // (1024 * 1024)
                print(f"ガベージコレクション後の利用可能メモリ: {available_mb} MB")
                
                if available_mb < 200:  # それでも200MB未満なら中止
                    print("❌ メモリ不足のため文字起こしを中止します")
                    return "メモリ不足により処理を中止しました"
        except Exception as e:
            print(f"メモリチェックエラー: {e}")
        
        try:
            # 音声ファイルの存在確認
            if not os.path.exists(filename):
                print(f"❌ 音声ファイルが見つかりません: {filename}")
                return None
            
            # ファイルサイズチェック
            file_size = os.path.getsize(filename)
            print(f"音声ファイルサイズ: {file_size / 1024:.1f} KB")
            
            if file_size == 0:
                print("❌ 音声ファイルが空です")
                return None
            
            # Whisperで文字起こし実行（安全化された設定）
            print(f"Whisperモデル({self.model_size})で文字起こし実行中...")
            
            result = self.model.transcribe(
                filename,
                language="ja",  # 日本語に設定
                fp16=False,     # 16bit浮動小数点を無効化（ARM64対応）
                verbose=False,  # 詳細ログを無効化してメモリ節約
                temperature=0,  # 温度を0に設定して一貫性を向上
                compression_ratio_threshold=2.4,  # 圧縮比の閾値
                logprob_threshold=-1.0,  # ログ確率の閾値
                no_speech_threshold=0.6,  # 無音判定の閾値
                condition_on_previous_text=False,  # 前のテキストに依存しない
                initial_prompt=None,  # 初期プロンプトなし
                word_timestamps=False,  # 単語レベルのタイムスタンプ無効
                prepend_punctuations="\"'"¿([{-",
                append_punctuations="\"'.。,，!！?？:：")]}、"
            )
            
            # 文字起こし後のメモリ使用量をチェック
            try:
                memory = psutil.virtual_memory()
                available_mb = memory.available // (1024 * 1024)
                print(f"文字起こし完了後の利用可能メモリ: {available_mb} MB")
            except:
                pass
            
            text = result["text"].strip() if result and "text" in result else ""
            
            if text:
                print(f"\n=== 文字起こし結果 ({self.model_size}モデル) ===")
                print(f"テキスト: {text}")
                print(f"時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 40)
            else:
                print("音声が検出されませんでした")
                
            # メモリクリーンアップ
            del result
            gc.collect()
                
            return text
            
        except MemoryError:
            print("❌ メモリ不足エラーが発生しました")
            print("💡 解決策:")
            print("   1. より軽量なモデル(tiny)を使用してください")
            print("   2. システムを再起動してメモリを解放してください")
            print("   3. スワップサイズを増やしてください")
            gc.collect()
            return "メモリ不足により処理に失敗しました"
            
        except RuntimeError as e:
            error_msg = str(e).lower()
            if "out of memory" in error_msg or "memory" in error_msg:
                print("❌ GPU/CPUメモリ不足エラーが発生しました")
                print("💡 解決策:")
                print("   1. tinyモデルを使用してください")
                print("   2. 他のプログラムを終了してメモリを確保してください")
                gc.collect()
                return "メモリ不足により処理に失敗しました"
            else:
                print(f"❌ 実行時エラー: {e}")
                print(f"詳細: {traceback.format_exc()}")
                return f"実行時エラー: {str(e)}"
                
        except Exception as e:
            print(f"❌ 文字起こしエラー: {e}")
            print(f"エラータイプ: {type(e).__name__}")
            print(f"詳細: {traceback.format_exc()}")
            
            # エラーの種類によって対処法を提案
            error_msg = str(e).lower()
            if "memory" in error_msg or "allocation" in error_msg:
                print("💡 メモリ関連エラーの可能性があります。軽量モデルを試してください。")
            elif "cuda" in error_msg or "gpu" in error_msg:
                print("💡 GPU関連エラーです。CPUモードで実行してください。")
            elif "audio" in error_msg or "format" in error_msg:
                print("💡 音声ファイル形式の問題の可能性があります。")
            
            gc.collect()
            return f"エラー: {str(e)}"
        
    def record_and_transcribe(self):
        """録音と文字起こしを実行"""
        temp_filename = None
        
        try:
            # 処理前のメモリ状況をチェック
            memory = psutil.virtual_memory()
            available_mb = memory.available // (1024 * 1024)
            print(f"処理開始前の利用可能メモリ: {available_mb} MB")
            
            if available_mb < 500:  # 500MB未満なら警告
                print("⚠️ 利用可能メモリが少なくなっています")
                print("💡 他のプログラムを終了することを推奨します")
            
            # 一時ファイル作成
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_filename = temp_file.name
            
            print(f"一時ファイル作成: {temp_filename}")
            
            # 録音実行
            print("=== 録音フェーズ ===")
            self.record_audio(temp_filename)
            
            # 録音後のファイル確認
            if not os.path.exists(temp_filename):
                print("❌ 録音ファイルが作成されませんでした")
                return None
            
            file_size = os.path.getsize(temp_filename)
            if file_size == 0:
                print("❌ 録音ファイルが空です")
                return None
            
            print(f"✅ 録音完了 (ファイルサイズ: {file_size / 1024:.1f} KB)")
            
            # 文字起こし実行
            print("=== 文字起こしフェーズ ===")
            text = self.transcribe_audio(temp_filename)
            
            return text
            
        except KeyboardInterrupt:
            print("\n⚠️ ユーザーによって処理が中断されました")
            return None
            
        except Exception as e:
            print(f"❌ 録音・文字起こし処理エラー: {e}")
            print(f"エラータイプ: {type(e).__name__}")
            print(f"詳細: {traceback.format_exc()}")
            return f"処理エラー: {str(e)}"
            
        finally:
            # 一時ファイル削除
            if temp_filename and os.path.exists(temp_filename):
                try:
                    os.unlink(temp_filename)
                    print(f"一時ファイル削除: {temp_filename}")
                except Exception as e:
                    print(f"一時ファイル削除エラー: {e}")
            
            # メモリクリーンアップ
            gc.collect()
    
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
        try:
            if hasattr(self, 'audio') and self.audio:
                self.audio.terminate()
                print("PyAudioリソースを解放しました")
        except Exception as e:
            print(f"リソース解放エラー: {e}")
        
        try:
            # モデルのメモリ解放
            if hasattr(self, 'model'):
                del self.model
            gc.collect()
        except Exception as e:
            print(f"モデルメモリ解放エラー: {e}")

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