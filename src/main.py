import argparse
import os
import tempfile

from dotenv import load_dotenv

from audio import record_wav
from transcribe import load_model, transcribe_file
from llm import setup_gemini, ask_gemini
from tts import initialize_tts, speak_text


def main():
    # .env ファイルから環境変数を読み込む
    load_dotenv()
    
    parser = argparse.ArgumentParser(description="Whisper + Gemini CLI for Raspberry Pi")
    parser.add_argument("-s", "--seconds", type=float, default=8.0, help="録音秒数（1ターン）")
    parser.add_argument("--model", default=os.getenv("WHISPER_MODEL", "small"), help="faster-whisperモデル名/パス（tiny/base/small等）")
    parser.add_argument(
        "--compute",
        default=os.getenv("WHISPER_COMPUTE", "int8"),
        choices=["int8", "int8_float32", "int16", "float32"],
        help="計算精度（INT8推奨）",
    )
    parser.add_argument("--lang", default=(os.getenv("LANG") or "ja")[:2], help="音声認識の言語コード（ja/en等）")
    parser.add_argument("--enable-tts", action="store_true", help="Voicevox音声出力を有効にする")
    parser.add_argument("--speaker-id", type=int, default=int(os.getenv("VOICEVOX_SPEAKER_ID", "1")), help="Voicevox話者ID")
    parser.add_argument(
        "--system",
        default=os.getenv("SYSTEM_PROMPT", """あなたは「マスク型・丁寧変換アシスタント」です。あなたの目的は、ユーザーからの短い発話（入力）を相手に失礼がなく、自然で丁寧な日本語の文章に“変換”して返すことです。

以下のルールを厳密に守ってください。
- 出力は必ず日本語とします。顔文字、絵文字、専門的な機械語は使用しないでください。
- 1文は60〜90文字程度に収め、読点（、）は1文に2つまでとして、簡潔にしてください。
- 文章の内容は、ユーザーの発話の意図を尊重しつつ、ビジネスシーンになりすぎずに、カジュアルで自然な日本語に変換してください。
- ユーザーの発話が質問や依頼の場合は、相手に失礼のないよう、丁寧な表現に変換してください。
- ユーザーの発話が否定的な内容の場合は、相手を不快にさせないよう、柔らかい表現に変換してください。
"""
        ),
        help="Geminiへのシステムプロンプト",
    )

    args = parser.parse_args()

    print("Whisperモデルを読み込み中...")
    load_model(args.model, args.compute)

    print("Geminiを初期化中...")
    model = setup_gemini()

    # 音声合成初期化（有効な場合）
    tts_enabled = False
    tts_engine = 'none'
    if args.enable_tts:
        print("音声合成を初期化中...")
        tts_enabled, tts_engine = initialize_tts(prefer_voicevox=True)
        if tts_enabled:
            engine_name = "Voicevox" if tts_engine == 'voicevox' else "Windows標準音声"
            print(f"✓ {engine_name}で音声出力が有効です")
        else:
            print("⚠ 音声合成の初期化に失敗しました（テキスト出力のみ）")

    print("準備完了。Enterで録音開始（Ctrl+Cで終了）")
    try:
        while True:
            input("Enter を押すと録音開始: ")
            wav_path = record_wav(args.seconds)
            try:
                text = transcribe_file(wav_path, language=args.lang)
            finally:
                try:
                    os.remove(wav_path)
                except OSError:
                    pass

            if not text:
                print("音声が認識できませんでした。もう一度お試しください。")
                continue

            print(f"あなた: {text}")
            reply = ask_gemini(model, text, system_prompt=args.system) or "(応答なし)"
            print(f"Gemini: {reply}")
            
            # 音声出力（有効な場合）
            if tts_enabled and reply.strip():
                speak_text(reply, args.speaker_id)

    except KeyboardInterrupt:
        print("\n終了します。")


if __name__ == "__main__":
    main()