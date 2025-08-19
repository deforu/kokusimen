#!/usr/bin/env python3
"""
音声デバイステスト用スクリプト
Raspberry Pi 5で音声入力デバイスを確認・テストする
"""

import pyaudio
import wave
import numpy as np
import time

def list_audio_devices():
    """利用可能な音声デバイスを一覧表示"""
    audio = pyaudio.PyAudio()
    
    print("利用可能な音声デバイス一覧:")
    print("=" * 60)
    
    device_count = audio.get_device_count()
    
    for i in range(device_count):
        device_info = audio.get_device_info_by_index(i)
        print(f"デバイス {i}:")
        print(f"  名前: {device_info['name']}")
        print(f"  最大入力チャンネル数: {device_info['maxInputChannels']}")
        print(f"  最大出力チャンネル数: {device_info['maxOutputChannels']}")
        print(f"  デフォルトサンプルレート: {device_info['defaultSampleRate']}")
        print("-" * 40)
    
    # デフォルトデバイス情報
    try:
        default_input = audio.get_default_input_device_info()
        print(f"デフォルト入力デバイス: {default_input['name']} (ID: {default_input['index']})")
    except:
        print("デフォルト入力デバイスが見つかりません")
    
    try:
        default_output = audio.get_default_output_device_info()
        print(f"デフォルト出力デバイス: {default_output['name']} (ID: {default_output['index']})")
    except:
        print("デフォルト出力デバイスが見つかりません")
    
    audio.terminate()

def test_microphone(device_id=None, duration=3):
    """マイクロフォンのテスト録音"""
    audio = pyaudio.PyAudio()
    
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    
    print(f"\n{duration}秒間のテスト録音を開始します...")
    if device_id is not None:
        print(f"使用デバイス ID: {device_id}")
    
    try:
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_id,
            frames_per_buffer=CHUNK
        )
        
        frames = []
        max_amplitude = 0
        
        for i in range(0, int(RATE / CHUNK * duration)):
            data = stream.read(CHUNK)
            frames.append(data)
            
            # 音量レベルをチェック
            audio_data = np.frombuffer(data, dtype=np.int16)
            current_amplitude = np.max(np.abs(audio_data))
            max_amplitude = max(max_amplitude, current_amplitude)
            
            # リアルタイム音量表示
            volume_bar = "█" * int(current_amplitude / 1000)
            print(f"\r音量: {volume_bar:<20} {current_amplitude:>6}", end="")
        
        print(f"\n録音完了")
        print(f"最大音量レベル: {max_amplitude}")
        
        if max_amplitude < 100:
            print("⚠️  音量が非常に小さいです。マイクの接続を確認してください。")
        elif max_amplitude < 1000:
            print("⚠️  音量が小さいです。マイクの音量を上げることを検討してください。")
        else:
            print("✅ 適切な音量レベルです。")
        
        stream.stop_stream()
        stream.close()
        
        # テスト録音を保存
        test_filename = "test_recording.wav"
        wf = wave.open(test_filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        print(f"テスト録音を {test_filename} に保存しました")
        
    except Exception as e:
        print(f"録音エラー: {e}")
    
    audio.terminate()

def audio_level_monitor(device_id=None):
    """リアルタイム音声レベルモニター"""
    audio = pyaudio.PyAudio()
    
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    
    print("リアルタイム音声レベルモニター (Ctrl+Cで終了)")
    if device_id is not None:
        print(f"使用デバイス ID: {device_id}")
    print("-" * 50)
    
    try:
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            input_device_index=device_id,
            frames_per_buffer=CHUNK
        )
        
        while True:
            data = stream.read(CHUNK)
            audio_data = np.frombuffer(data, dtype=np.int16)
            amplitude = np.max(np.abs(audio_data))
            
            # 音量バーの表示
            bar_length = int(amplitude / 1000)
            volume_bar = "█" * min(bar_length, 50)
            
            print(f"\r音量: [{volume_bar:<50}] {amplitude:>6}", end="")
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nモニター終了")
    except Exception as e:
        print(f"\nエラー: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

def main():
    """メイン関数"""
    print("Raspberry Pi 5 音声デバイステストツール")
    print("=" * 50)
    
    while True:
        print("\n選択してください:")
        print("1. 音声デバイス一覧表示")
        print("2. マイクロフォンテスト録音")
        print("3. 特定デバイスでテスト録音")
        print("4. リアルタイム音声レベルモニター")
        print("5. 終了")
        
        choice = input("選択 (1-5): ").strip()
        
        if choice == "1":
            list_audio_devices()
        elif choice == "2":
            test_microphone()
        elif choice == "3":
            try:
                device_id = int(input("デバイスIDを入力: "))
                test_microphone(device_id)
            except ValueError:
                print("無効なデバイスIDです")
        elif choice == "4":
            device_input = input("デバイスID (Enterでデフォルト): ").strip()
            device_id = int(device_input) if device_input else None
            audio_level_monitor(device_id)
        elif choice == "5":
            print("プログラムを終了します")
            break
        else:
            print("無効な選択です")

if __name__ == "__main__":
    main()