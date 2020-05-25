import main
import unittest.mock as mock
import pytest

# b2 01 4b 46 7f ff 0e 10 8c : crc=8c YES\nb2 01 4b 46 7f ff 0e 10 8c t=27125\n

@pytest.mark.parametrize("sensor_output,expected", [
    ("b2 01 4b 46 7f ff 0e 10 8c : crc=8c YES\nb2 01 4b 46 7f ff 0e 10 8c t=28875\n", 28.875),
    ("b2 01 4b 46 7f ff 0e 10 8c : crc=8c YES\nb2 01 4b 46 7f ff 0e 10 8c t=1234\n", 1.234),
    ("b2 01 4b 46 7f ff 0e 10 8c : crc=8c YES\nb2 01 4b 46 7f ff 0e 10 8c t=0\n", 0),
    ("b2 01 4b 46 7f ff 0e 10 8c : crc=8c YES\nb2 01 4b 46 7f ff 0e 10 8c t=-5250\n", -5.25),
    ("b2 01 4b 46 7f ff 0e 10 8c : crc=8c YES\nb2 01 4b 46 7f ff 0e 10 8c t=-10250\n", -10.25),
    ("b2 01 4b 46 7f ff 0e 10 8c : crc=8c NO", None),
])
def test_get_temperature_from_id(sensor_output, expected):
    with mock.patch("builtins.open", mock.mock_open(read_data=sensor_output)):
        actual = main.get_temperature_from_id("4cdf645")

        assert actual == expected