"""
Windows標準音声合成モジュール - SAPI連携
"""
import os
import sys
from typing import Optional

try:
    import win32com.client
    SAPI_AVAILABLE = True
except ImportError:
    SAPI_AVAILABLE = False


class WindowsTTS:
    def __init__(self):
        """Windows SAPI音声合成クライアント初期化"""
        self.sapi = None
        self.available = False
        
        if SAPI_AVAILABLE:
            try:
                self.sapi = win32com.client.Dispatch("SAPI.SpVoice")
                self.available = True
            except Exception as e:
                print(f"⚠ Windows音声合成の初期化に失敗: {e}")
        else:
            print("⚠ pywin32が必要です: pip install pywin32")
    
    def is_available(self) -> bool:
        """音声合成が利用可能かチェック"""
        return self.available
    
    def get_voices(self) -> list:
        """利用可能な音声一覧を取得"""
        if not self.available:
            return []
        
        try:
            voices = []
            voice_tokens = self.sapi.GetVoices()
            for i in range(voice_tokens.Count):
                voice = voice_tokens.Item(i)
                voices.append({
                    'id': i,
                    'name': voice.GetDescription(),
                    'language': voice.GetAttribute('Language') or 'Unknown'
                })
            return voices
        except Exception as e:
            print(f"音声一覧取得エラー: {e}")
            return []
    
    def speak(self, text: str, voice_id: int = None, rate: int = 0) -> bool:
        """
        テキストを音声で読み上げ
        
        Args:
            text: 読み上げるテキスト
            voice_id: 音声ID（None=デフォルト）
            rate: 話速（-10〜10、0=標準）
        """
        if not self.available or not text.strip():
            return False
        
        try:
            # 音声選択
            if voice_id is not None:
                voices = self.sapi.GetVoices()
                if 0 <= voice_id < voices.Count:
                    self.sapi.Voice = voices.Item(voice_id)
            
            # 話速設定
            self.sapi.Rate = max(-10, min(10, rate))
            
            print(f"🔊 音声出力中: {text[:30]}...")
            self.sapi.Speak(text)
            return True
            
        except Exception as e:
            print(f"音声出力エラー: {e}")
            return False


# グローバルTTSインスタンス
_windows_tts: Optional[WindowsTTS] = None


def initialize_windows_tts() -> bool:
    """Windows音声合成を初期化"""
    global _windows_tts
    
    _windows_tts = WindowsTTS()
    
    if not _windows_tts.is_available():
        return False
    
    print("✓ Windows標準音声合成が利用可能です")
    return True


def speak_with_sapi(text: str, voice_id: int = None, rate: int = 0) -> bool:
    """Windows SAPI でテキストを読み上げ"""
    if _windows_tts is None:
        return False
    
    return _windows_tts.speak(text, voice_id, rate)


def get_windows_voices() -> list:
    """Windows音声一覧を取得"""
    if _windows_tts is None:
        return []
    return _windows_tts.get_voices()