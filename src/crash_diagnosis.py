#!/usr/bin/env python3
"""
Whisperクラッシュ診断ツール
システム環境とWhisperの互換性をチェックし、クラッシュの原因を特定
"""

import os
import sys
import subprocess
import platform
import psutil
import tempfile
import traceback

def check_system_info():
    """システム情報をチェック"""
    print("=== システム情報 ===")
    
    # OS情報
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"アーキテクチャ: {platform.machine()}")
    print(f"Python バージョン: {sys.version}")
    
    # CPU情報
    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpu_info = f.read()
            if 'BCM2835' in cpu_info or 'BCM2711' in cpu_info or 'BCM2712' in cpu_info:
                if 'BCM2712' in cpu_info:
                    print("CPU: Raspberry Pi 5 (BCM2712)")
                elif 'BCM2711' in cpu_info:
                    print("CPU: Raspberry Pi 4 (BCM2711)")
                else:
                    print("CPU: 古いRaspberry Pi")
            else:
                print("CPU: その他")
    except:
        print("CPU: 情報取得不可")
    
    # メモリ情報
    memory = psutil.virtual_memory()
    print(f"総メモリ: {memory.total // (1024**3)} GB")
    print(f"利用可能メモリ: {memory.available // (1024**2)} MB")
    print(f"メモリ使用率: {memory.percent}%")
    
    # スワップ情報
    swap = psutil.swap_memory()
    print(f"スワップ容量: {swap.total // (1024**2)} MB")
    print(f"スワップ使用: {swap.used // (1024**2)} MB")
    
    print()

def check_python_packages():
    """Pythonパッケージの互換性をチェック"""
    print("=== Pythonパッケージチェック ===")
    
    required_packages = [
        'torch',
        'torchaudio', 
        'whisper',
        'numpy',
        'pyaudio',
        'psutil'
    ]
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}: インストール済み")
        except ImportError:
            print(f"❌ {package}: 未インストール")
        except Exception as e:
            print(f"⚠️ {package}: エラー - {e}")
    
    print()

def test_whisper_models():
    """Whisperモデルのテスト読み込み"""
    print("=== Whisperモデルテスト ===")
    
    models = ['tiny', 'base', 'small']
    
    for model_name in models:
        print(f"{model_name}モデルをテスト中...")
        
        try:
            # メモリ使用量を監視
            process = psutil.Process()
            memory_before = process.memory_info().rss / (1024**2)
            
            import whisper
            model = whisper.load_model(model_name, device="cpu")
            
            memory_after = process.memory_info().rss / (1024**2)
            memory_diff = memory_after - memory_before
            
            print(f"✅ {model_name}: 読み込み成功 (メモリ使用量: +{memory_diff:.1f} MB)")
            
            # モデルを削除してメモリ解放
            del model
            import gc
            gc.collect()
            
        except MemoryError:
            print(f"❌ {model_name}: メモリ不足で読み込み失敗")
        except Exception as e:
            print(f"❌ {model_name}: エラー - {e}")
            print(f"   詳細: {traceback.format_exc()}")
    
    print()

def test_audio_system():
    """音声システムのテスト"""
    print("=== 音声システムテスト ===")
    
    try:
        import pyaudio
        
        audio = pyaudio.PyAudio()
        print(f"PyAudio初期化: 成功")
        print(f"利用可能デバイス数: {audio.get_device_count()}")
        
        # デフォルト入力デバイスチェック
        try:
            default_input = audio.get_default_input_device_info()
            print(f"デフォルト入力デバイス: {default_input['name']}")
            print(f"最大入力チャンネル: {default_input['maxInputChannels']}")
        except:
            print("⚠️ デフォルト入力デバイスが見つかりません")
        
        audio.terminate()
        
    except Exception as e:
        print(f"❌ PyAudioエラー: {e}")
    
    # ALSAデバイスチェック
    try:
        result = subprocess.run(['arecord', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            print("ALSA録音デバイス:")
            print(result.stdout)
        else:
            print("⚠️ ALSA録音デバイスが見つかりません")
    except:
        print("⚠️ arecordコマンドが利用できません")
    
    print()

def test_whisper_transcription():
    """実際の文字起こしテスト"""
    print("=== 文字起こしテスト ===")
    
    try:
        # 無音の音声ファイルを作成してテスト
        import numpy as np
        import wave
        
        # 5秒間の無音ファイルを作成
        sample_rate = 16000
        duration = 2  # 2秒に短縮
        samples = np.zeros(int(sample_rate * duration), dtype=np.int16)
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        # WAVファイルとして保存
        with wave.open(temp_filename, 'w') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(samples.tobytes())
        
        print("テスト音声ファイル作成完了")
        
        # Whisperで文字起こしテスト
        import whisper
        
        for model_name in ['tiny', 'base']:
            try:
                print(f"{model_name}モデルで文字起こしテスト中...")
                
                # メモリ監視
                process = psutil.Process()
                memory_before = process.memory_info().rss / (1024**2)
                
                model = whisper.load_model(model_name, device="cpu")
                result = model.transcribe(
                    temp_filename,
                    language="ja",
                    fp16=False,
                    verbose=False
                )
                
                memory_after = process.memory_info().rss / (1024**2)
                memory_diff = memory_after - memory_before
                
                print(f"✅ {model_name}: 文字起こし成功 (メモリ使用量: +{memory_diff:.1f} MB)")
                print(f"   結果: '{result['text']}'")
                
                # クリーンアップ
                del model, result
                import gc
                gc.collect()
                
                break  # 1つでも成功したら終了
                
            except Exception as e:
                print(f"❌ {model_name}: 文字起こしエラー - {e}")
                if "memory" in str(e).lower():
                    print("   → メモリ不足が原因の可能性")
                if "cuda" in str(e).lower():
                    print("   → GPU関連エラー（CPUモードを使用してください）")
        
        # テストファイル削除
        try:
            os.unlink(temp_filename)
        except:
            pass
            
    except Exception as e:
        print(f"❌ 文字起こしテスト失敗: {e}")
        print(f"詳細: {traceback.format_exc()}")
    
    print()

def suggest_solutions():
    """解決策の提案"""
    print("=== 推奨解決策 ===")
    
    memory = psutil.virtual_memory()
    available_gb = memory.available / (1024**3)
    
    if available_gb < 1:
        print("❌ メモリ不足 (1GB未満)")
        print("解決策:")
        print("  1. 他のプログラムを終了してメモリを解放")
        print("  2. スワップサイズを増やす:")
        print("     sudo dphys-swapfile swapoff")
        print("     sudo nano /etc/dphys-swapfile  # CONF_SWAPSIZE=2048")
        print("     sudo dphys-swapfile setup")
        print("     sudo dphys-swapfile swapon")
        print("  3. tinyモデルのみ使用")
        
    elif available_gb < 2:
        print("⚠️ メモリ少なめ (2GB未満)")
        print("推奨:")
        print("  1. tinyまたはbaseモデルを使用")
        print("  2. 他のプログラムを最小限に")
        
    else:
        print("✅ メモリ十分")
        print("  すべてのモデルが使用可能")
    
    # Raspberry Pi固有の最適化
    try:
        with open('/proc/device-tree/model', 'r') as f:
            model_info = f.read()
            if 'Raspberry Pi' in model_info:
                print("\nRaspberry Pi最適化:")
                print("  1. GPU メモリ分割: sudo raspi-config > Advanced > Memory Split > 128")
                print("  2. CPUパフォーマンス: echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor")
                print("  3. 不要なサービス停止: sudo systemctl disable bluetooth")
    except:
        pass
    
    print()

def main():
    """メイン診断関数"""
    print("🔍 Whisperクラッシュ診断ツール")
    print("=" * 50)
    
    check_system_info()
    check_python_packages()
    test_audio_system()
    test_whisper_models()
    test_whisper_transcription()
    suggest_solutions()
    
    print("診断完了！")
    print("問題が解決しない場合は、この出力をGitHubのIssueに投稿してください。")

if __name__ == "__main__":
    main()