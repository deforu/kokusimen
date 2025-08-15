"""
音声合成話者情報表示ツール（Voicevox/Windows対応）
"""
import sys
import os

# srcディレクトリをPythonパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from dotenv import load_dotenv
from tts import initialize_tts, get_available_voices


def main():
    load_dotenv()
    
    print("🎭 音声合成 話者/音声情報")
    print("=" * 50)
    
    # 音声合成エンジン初期化
    success, engine = initialize_tts(prefer_voicevox=True)
    
    if not success:
        print("❌ 音声合成エンジンに接続できませんでした")
        print("\n利用可能な音声合成:")
        print("1. Voicevox（高品質）")
        print("   - ダウンロード: https://voicevox.hiroshiba.jp/")
        print("   - 起動後、このスクリプトを再実行")
        print()
        print("2. Windows標準音声（内蔵）")
        print("   - pywin32をインストール: pip install pywin32")
        return 1
    
    voices_info = get_available_voices()
    voices = voices_info.get('voices', [])
    engine_name = voices_info.get('engine', 'unknown')
    
    if not voices:
        print("話者情報を取得できませんでした")
        return 1
    
    print(f"🔊 使用エンジン: {engine_name.upper()}")
    print("利用可能な音声:")
    print()
    
    if engine_name == 'voicevox':
        # Voicevox形式で表示
        for speaker in voices:
            speaker_name = speaker.get("name", "不明")
            print(f"📢 {speaker_name}")
            
            for style in speaker.get("styles", []):
                style_name = style.get("name", "不明")
                style_id = style.get("id", "?")
                print(f"   - {style_name} (ID: {style_id})")
            print()
    
    elif engine_name == 'windows':
        # Windows SAPI形式で表示
        for voice in voices:
            voice_id = voice.get('id', '?')
            voice_name = voice.get('name', '不明')
            language = voice.get('language', '不明')
            print(f"🔊 ID {voice_id}: {voice_name}")
            print(f"   言語: {language}")
            print()
    
    print("=" * 50)
    print("使用方法:")
    if engine_name == 'voicevox':
        print(f"python src\\main.py --enable-tts --speaker-id [ID番号]")
        print()
        print("例: 四国めたん（ノーマル）を使用")
        print("python src\\main.py --enable-tts --speaker-id 1")
    else:
        print(f"python src\\main.py --enable-tts --speaker-id [ID番号]")
        print()
        print("例: Windows標準音声を使用")
        print("python src\\main.py --enable-tts --speaker-id 0")


if __name__ == "__main__":
    sys.exit(main())