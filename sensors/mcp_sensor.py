import sensors.base_sensor
import typing_extensions


class MCPProtocol(typing_extensions.Protocol):
    def read_adc(self, channel: int) -> int:
        ...


class MCPSensor(sensors.base_sensor.BaseSensor):
    _mcp: MCPProtocol
    _channel: int

    def __init__(self, name: str, mcp3xxx: MCPProtocol, channel: int):
        self._mcp = mcp3xxx

        self._channel = channel

        super().__init__(name)

    @property
    def value(self):
        return self._mcp.read_adc(self._channel)

    @property
    def channel(self):
        return self._channel

    @channel.setter
    def channel(self, channel: int):
        if not 0 <= channel <= 7:
            raise ValueError("channel must be between 0 and 7 inclusive!")

        self._channel = channel
