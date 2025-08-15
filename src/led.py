import time
from typing import Tuple

_rpi_ws281x_installed = True
try:
    from rpi_ws281x import PixelStrip, Color
except ImportError:
    _rpi_ws281x_installed = False

    class _DummyPixelStrip:
        def __init__(self, *args, **kwargs):
            print("rpi_ws281x is not installed. Using a dummy PixelStrip.")

        def begin(self):
            pass

        def setPixelColor(self, n, color):
            pass

        def show(self):
            pass

        def numPixels(self):
            return 0

    def _DummyColor(r, g, b):
        return (r, g, b)


# LED strip configuration (仮設定)
LED_COUNT = 8  # LEDの数
LED_PIN = 18  # GPIO pin connected to the pixels (must support PWM!)
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10  # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 128  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False  # True to invert the signal (when using NPN transistor level shift)

# カラー定義
COLOR_POSITIVE: Tuple[int, int, int] = (0, 255, 0)  # Green
COLOR_NEGATIVE: Tuple[int, int, int] = (255, 0, 0)  # Red
COLOR_NEUTRAL: Tuple[int, int, int] = (255, 255, 255)  # White
COLOR_OFF: Tuple[int, int, int] = (0, 0, 0)  # Off

_strip = None


def setup_leds() -> None:
    """Initialize the LED strip."""
    global _strip
    if _rpi_ws281x_installed:
        _strip = PixelStrip(
            LED_COUNT,
            LED_PIN,
            LED_FREQ_HZ,
            LED_DMA,
            LED_INVERT,
            LED_BRIGHTNESS,
        )
        _strip.begin()
    else:
        _strip = _DummyPixelStrip()


def set_led_color(color: Tuple[int, int, int], duration_sec: float = 3.0) -> None:
    """Set the color of all LEDs for a given duration."""
    if _strip is None:
        return

    if not _rpi_ws281x_installed:
        print(f"Dummy LED: Setting color to {color}")
        return

    r, g, b = color
    for i in range(_strip.numPixels()):
        _strip.setPixelColor(i, Color(r, g, b))
    _strip.show()

    if duration_sec > 0:
        time.sleep(duration_sec)
        clear_leds()


def clear_leds() -> None:
    """Turn off all LEDs."""
    if _strip is None:
        return

    if not _rpi_ws281x_installed:
        print("Dummy LED: Clearing LEDs")
        return

    r, g, b = COLOR_OFF
    for i in range(_strip.numPixels()):
        _strip.setPixelColor(i, Color(r, g, b))
    _strip.show()
