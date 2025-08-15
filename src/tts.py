"""
音声合成モジュール - Voicevox/Windows SAPI連携
"""
import json
import requests
import tempfile
import os
from typing import Optional
import pygame

from tts_windows import initialize_windows_tts, speak_with_sapi, get_windows_voices


class VoicevoxClient:
    def __init__(self, base_url: str = "http://127.0.0.1:50021"):
        """
        Voicevoxクライアント初期化
        
        Args:
            base_url: VoicevoxエンジンのベースURL（通常はlocalhost:50021）
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 10
        
        # pygame mixer初期化（音声再生用）
        try:
            pygame.mixer.init()
            self.audio_available = True
        except:
            print("⚠ 音声出力が利用できません")
            self.audio_available = False
    
    def is_available(self) -> bool:
        """Voicevoxエンジンが利用可能かチェック"""
        try:
            response = self.session.get(f"{self.base_url}/version", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def get_speakers(self) -> list:
        """利用可能な話者一覧を取得"""
        try:
            response = self.session.get(f"{self.base_url}/speakers")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"話者一覧取得エラー: {e}")
            return []
    
    def text_to_speech(self, text: str, speaker_id: int = 1, speed: float = 1.0, 
                      pitch: float = 0.0, intonation: float = 1.0) -> Optional[bytes]:
        """
        テキストを音声に変換
        
        Args:
            text: 音声化するテキスト
            speaker_id: 話者ID（1: 四国めたん（ノーマル）など）
            speed: 話速（0.5-2.0）
            pitch: 音高（-0.15-0.15）
            intonation: 抑揚（0.0-2.0）
            
        Returns:
            音声データ（wav形式のバイト列）
        """
        try:
            # 1. 音声クエリ作成
            query_params = {
                "text": text,
                "speaker": speaker_id
            }
            response = self.session.post(
                f"{self.base_url}/audio_query", 
                params=query_params
            )
            response.raise_for_status()
            
            # 2. クエリ調整
            query_data = response.json()
            query_data["speedScale"] = speed
            query_data["pitchScale"] = pitch
            query_data["intonationScale"] = intonation
            
            # 3. 音声合成
            synthesis_params = {"speaker": speaker_id}
            response = self.session.post(
                f"{self.base_url}/synthesis",
                params=synthesis_params,
                headers={"Content-Type": "application/json"},
                data=json.dumps(query_data)
            )
            response.raise_for_status()
            
            return response.content
            
        except Exception as e:
            print(f"音声合成エラー: {e}")
            return None
    
    def play_audio(self, audio_data: bytes) -> bool:
        """音声データを再生"""
        if not self.audio_available or not audio_data:
            return False
            
        try:
            # 一時ファイルに保存して再生
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_file:
                tmp_file.write(audio_data)
                tmp_path = tmp_file.name
            
            pygame.mixer.music.load(tmp_path)
            pygame.mixer.music.play()
            
            # 再生完了まで待機
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            # 一時ファイル削除
            os.unlink(tmp_path)
            return True
            
        except Exception as e:
            print(f"音声再生エラー: {e}")
            return False
    
    def speak(self, text: str, speaker_id: int = 1, **kwargs) -> bool:
        """テキストを音声で読み上げ"""
        if not text.strip():
            return False
            
        print(f"🔊 音声合成中: {text[:30]}...")
        
        audio_data = self.text_to_speech(text, speaker_id, **kwargs)
        if audio_data:
            return self.play_audio(audio_data)
        
        return False


# グローバル音声合成設定
_tts_engine = None  # 'voicevox' または 'windows'
_voicevox_client: Optional[VoicevoxClient] = None


def initialize_tts(prefer_voicevox: bool = True) -> tuple[bool, str]:
    """
    音声合成エンジンを初期化
    
    Args:
        prefer_voicevox: Voicevoxを優先するか
        
    Returns:
        (成功フラグ, 使用エンジン名)
    """
    global _tts_engine, _voicevox_client
    
    if prefer_voicevox:
        # 1. Voicevoxを試行
        base_url = os.getenv("VOICEVOX_URL", "http://127.0.0.1:50021")
        _voicevox_client = VoicevoxClient(base_url)
        
        if _voicevox_client.is_available():
            _tts_engine = 'voicevox'
            print("✓ Voicevox音声合成が利用可能です")
            return True, 'voicevox'
    
    # 2. Windows標準音声合成を試行
    if initialize_windows_tts():
        _tts_engine = 'windows'
        print("✓ Windows標準音声合成を使用します")
        return True, 'windows'
    
    print("⚠ 音声合成エンジンが利用できません")
    return False, 'none'


def initialize_voicevox(base_url: str = None) -> bool:
    """Voicevoxクライアントを初期化（後方互換用）"""
    success, engine = initialize_tts(prefer_voicevox=True)
    return success and engine == 'voicevox'


def speak_text(text: str, speaker_id: int = None, **kwargs) -> bool:
    """
    テキストを音声で読み上げ（統合関数）
    
    Args:
        text: 読み上げるテキスト
        speaker_id: 話者/音声ID
        **kwargs: エンジン固有のオプション
    """
    if not text.strip():
        return False
    
    if _tts_engine == 'voicevox' and _voicevox_client:
        if speaker_id is None:
            speaker_id = int(os.getenv("VOICEVOX_SPEAKER_ID", "1"))
        return _voicevox_client.speak(text, speaker_id, **kwargs)
    
    elif _tts_engine == 'windows':
        voice_id = speaker_id if speaker_id is not None else int(os.getenv("WINDOWS_VOICE_ID", "0"))
        rate = kwargs.get('rate', 0)  # 話速
        return speak_with_sapi(text, voice_id, rate)
    
    print("音声合成エンジンが初期化されていません")
    return False


def get_available_voices() -> dict:
    """利用可能な音声一覧を取得"""
    result = {'engine': _tts_engine, 'voices': []}
    
    if _tts_engine == 'voicevox' and _voicevox_client:
        result['voices'] = _voicevox_client.get_speakers()
    elif _tts_engine == 'windows':
        result['voices'] = get_windows_voices()
    
    return result


def get_available_speakers() -> list:
    """利用可能な話者一覧を取得（後方互換用）"""
    voices = get_available_voices()
    return voices.get('voices', [])