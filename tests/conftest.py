import sys
import unittest.mock as mock

sys.modules["Adafruit_GPIO.SPI"] = mock.MagicMock()
sys.modules["Adafruit_GPIO"] = mock.MagicMock()
sys.modules["Adafruit_MCP3008"] = mock.MagicMock()
sys.modules["wiringpi"] = mock.MagicMock()
