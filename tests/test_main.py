import sys
import unittest.mock as mock
import main
import sensors.base_sensor
import controllers.base_controller
import pytest
import datetime
import queue
import mongomock

@pytest.fixture
def mock_sensor():
    return mock.MagicMock(spec=sensors.base_sensor.BaseSensor)


@pytest.fixture
def mock_controller():
    return mock.MagicMock(spec=controllers.base_controller.BaseController)


@mock.patch("main.open", new=mock.MagicMock())
def test_process(mock_sensor, mock_controller):
    mock_sensor.value = 10
    mock_controller.value = 0
    main.process(sensors=[mock_sensor], controllers=[mock_controller])

@mock.patch(
    "sensors.ds18b20.DS18B20._check_device_exists",
    new=mock.MagicMock(return_value=True),
)
@mock.patch("main.atexit")
@mock.patch("main.Loop")
@mock.patch("main.process")
def test_main(process, loop, atexit):
    main.main()

    loop.return_value.start.assert_called_once()
    atexit.register.assert_called_once()
