"""
環境チェックスクリプト - 黒死面プロジェクト
"""
import sys
import os

# srcディレクトリをPythonパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_python_version():
    """Python バージョンをチェック"""
    version = sys.version_info
    print(f"✓ Python バージョン: {version.major}.{version.minor}.{version.micro}")
    if version < (3, 9):
        print("⚠ 警告: Python 3.9以上を推奨します")
        return False
    return True

def check_packages():
    """必要なパッケージの確認"""
    required_packages = [
        'faster_whisper',
        'google.generativeai',
        'sounddevice',
        'soundfile',
        'dotenv',
        'requests',
        'pygame'
    ]
    
    print("\n=== パッケージチェック ===")
    all_ok = True
    
    for package in required_packages:
        try:
            if package == 'dotenv':
                from dotenv import load_dotenv
            else:
                __import__(package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} - インストールが必要")
            all_ok = False
    
    # pywin32チェック（Windows音声合成用）
    try:
        import win32com.client
        print("✓ pywin32 (Windows音声合成)")
    except ImportError:
        print("⚠ pywin32 - Windows音声合成に必要（オプション）")
    
    return all_ok

def check_audio_devices():
    """オーディオデバイスの確認"""
    print("\n=== オーディオデバイスチェック ===")
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        print(f"✓ 入力デバイス数: {len(input_devices)}")
        
        if input_devices:
            default_input = sd.query_devices(kind='input')
            print(f"✓ デフォルト入力: {default_input['name']}")
        else:
            print("⚠ 警告: 入力デバイスが見つかりません")
            return False
        
        return True
    except Exception as e:
        print(f"✗ オーディオデバイスチェックエラー: {e}")
        return False

def check_environment():
    """環境変数の確認"""
    print("\n=== 環境変数チェック ===")
    from dotenv import load_dotenv
    load_dotenv()
    
    gemini_key = os.getenv('GEMINI_API_KEY')
    if gemini_key:
        masked_key = gemini_key[:8] + '*' * (len(gemini_key) - 12) + gemini_key[-4:] if len(gemini_key) > 12 else '***'
        print(f"✓ GEMINI_API_KEY: {masked_key}")
        return True
    else:
        print("✗ GEMINI_API_KEY が設定されていません")
        print("  設定方法:")
        print("  1. .env ファイルに GEMINI_API_KEY=your_key_here を追加")
        print("  2. または環境変数で $env:GEMINI_API_KEY='your_key_here' (PowerShell)")
        return False

def test_whisper_model():
    """Whisperモデルのロードテスト"""
    print("\n=== Whisperモデルテスト ===")
    try:
        from transcribe import load_model
        print("Whisperモデル（tiny）をロード中...")
        load_model("tiny", "int8")
        print("✓ Whisperモデルのロード成功")
        return True
    except Exception as e:
        print(f"✗ Whisperモデルのロードエラー: {e}")
        return False

def test_gemini_connection():
    """Gemini接続テスト"""
    print("\n=== Gemini接続テスト ===")
    try:
        from llm import setup_gemini, ask_gemini
        model = setup_gemini()
        print("✓ Gemini接続成功")
        
        # 簡単なテスト
        response = ask_gemini(model, "こんにちは", "簡潔に挨拶を返してください。")
        if response:
            print(f"✓ Gemini応答テスト成功: {response[:50]}...")
            return True
        else:
            print("⚠ Gemini応答が空です")
            return False
            
    except Exception as e:
        print(f"✗ Gemini接続エラー: {e}")
        return False

def test_tts_engines():
    """音声合成エンジンのテスト"""
    print("\n=== 音声合成エンジンテスト ===")
    try:
        from tts import initialize_tts, get_available_voices
        
        # 音声合成初期化を試行
        success, engine = initialize_tts(prefer_voicevox=True)
        
        if success:
            if engine == 'voicevox':
                print("✓ Voicevoxエンジン接続成功")
            elif engine == 'windows':
                print("✓ Windows標準音声合成が利用可能")
            
            voices_info = get_available_voices()
            voices = voices_info.get('voices', [])
            if voices:
                print(f"✓ 利用可能音声数: {len(voices)}")
                return True
            else:
                print("⚠ 音声情報を取得できません")
                return False
        else:
            print("⚠ 音声合成エンジンが利用できません")
            print("  - Voicevox: 起動していない、またはURL不正")
            print("  - Windows音声: pywin32未インストール")
            return False
            
    except Exception as e:
        print(f"✗ 音声合成テストエラー: {e}")
        return False

def main():
    print("🎭 黒死面 - 環境チェック")
    print("=" * 40)
    
    checks = [
        ("Python バージョン", check_python_version),
        ("パッケージ", check_packages),
        ("オーディオデバイス", check_audio_devices),
        ("環境変数", check_environment),
        ("Whisperモデル", test_whisper_model),
        ("Gemini接続", test_gemini_connection),
        ("音声合成エンジン", test_tts_engines),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except KeyboardInterrupt:
            print("\n\n中断されました")
            sys.exit(1)
        except Exception as e:
            print(f"✗ {name}チェック中にエラー: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 40)
    print("📋 チェック結果まとめ")
    print("=" * 40)
    
    all_passed = True
    for name, passed in results:
        status = "✓ 成功" if passed else "✗ 失敗"
        print(f"{name:15} : {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 40)
    if all_passed:
        print("🎉 全てのチェックが完了しました！")
        print("次のコマンドでプログラムを実行できます:")
        print("テキスト出力のみ:")
        print("python src\\main.py -s 4 --model small")
        print("\n音声出力付き:")
        print("python src\\main.py -s 4 --model small --enable-tts")
    else:
        print("⚠ いくつかの問題があります。上記の結果を確認してください。")
        print("\n📝 音声合成が利用できない場合でも、テキスト出力は可能です。")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())