import os
import tempfile

import sounddevice as sd
import soundfile as sf


def record_wav(duration_sec: float = 8.0, samplerate: int = 16000, channels: int = 1) -> str:
    """Record audio from default input and save to a temporary WAV file.

    Returns the file path to the WAV file.
    """
    if duration_sec <= 0:
        raise ValueError("duration_sec must be > 0")

    print(f"録音中... {duration_sec:.1f} 秒（Ctrl+Cで中断）")
    recording = sd.rec(int(duration_sec * samplerate), samplerate=samplerate, channels=channels, dtype="int16")
    sd.wait()

    fd, path = tempfile.mkstemp(prefix="rec_", suffix=".wav")
    os.close(fd)
    sf.write(path, recording, samplerate, subtype="PCM_16")
    return path

