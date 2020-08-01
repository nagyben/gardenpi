from sensors import DS18B20
import pytest
import numpy
import unittest.mock as mock


def test_device_not_found():
    with pytest.raises(IOError):
        DS18B20(name="t_ds18_0", id="abcdef12")


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
@mock.patch.object(
    DS18B20, "_check_device_exists", new=mock.MagicMock(return_value=True)
)
def test_get_value(sensor_output, expected):
    t = DS18B20(name="t_ds18_0", id="abcdef12")
    with mock.patch("builtins.open", mock.mock_open(read_data=sensor_output)):
        t.update()
        actual = t.value

        if numpy.isnan(expected):
            assert numpy.isnan(actual)
        else:
            assert actual == expected
