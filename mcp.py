import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import time

# Hardware SPI configuration:
SPI_PORT   = 0
SPI_DEVICE = 0
MCP = Adafruit_MCP3008.MCP3008(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

def readmcp():
    return MCP.read_adc(0)