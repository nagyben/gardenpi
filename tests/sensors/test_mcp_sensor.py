import unittest.mock as mock
from sensors.base_sensor import BaseSensor
from sensors import MCPSensor


class MockMCP:
    def read_adc(self, channel: int):
        return channel


def test_mcp_sensor():
    m = MCPSensor(name="lux", mcp3xxx=MockMCP(), channel=0)

    assert m.value == 0
