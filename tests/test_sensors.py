import sensors
import unittest.mock as mock
import pytest
import numpy


@pytest.mark.parametrize(
    "sensor_output,expected",
    [
        (
            "b2 01 4b 46 7f ff 0e 10 8c : crc=8c YES\nb2 01 4b 46 7f ff 0e 10 8c t=28875\n",
            28.875,
        ),
        (
            "b2 01 4b 46 7f ff 0e 10 8c : crc=8c YES\nb2 01 4b 46 7f ff 0e 10 8c t=1234\n",
            1.234,
        ),
        (
            "b2 01 4b 46 7f ff 0e 10 8c : crc=8c YES\nb2 01 4b 46 7f ff 0e 10 8c t=0\n",
            0,
        ),
        (
            "b2 01 4b 46 7f ff 0e 10 8c : crc=8c YES\nb2 01 4b 46 7f ff 0e 10 8c t=-5250\n",
            -5.25,
        ),
        (
            "b2 01 4b 46 7f ff 0e 10 8c : crc=8c YES\nb2 01 4b 46 7f ff 0e 10 8c t=-10250\n",
            -10.25,
        ),
        ("b2 01 4b 46 7f ff 0e 10 8c : crc=8c NO", numpy.nan),
    ],
)
def test_get_temperature_from_id(sensor_output, expected):
    with mock.patch("builtins.open", mock.mock_open(read_data=sensor_output)):
        actual = sensors.get_temperature_from_id("4cdf645")

        if numpy.isnan(expected):
            assert numpy.isnan(actual)
        else:
            assert actual == expected


class MockMCP:
    gen = (x for x in range(1, 6))

    def readmcp(self, channel):
        return next(self.gen)


@mock.patch("time.sleep", new=mock.MagicMock())
@mock.patch("sensors.mcp", new=MockMCP())
def test_get_lux():
    actual = sensors.get_lux()
    assert actual == 3
