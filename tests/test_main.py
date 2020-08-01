import main
import unittest.mock as mock
import sensors.base_sensor
import controllers.base_controller
import pytest
import datetime


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


@mock.patch("main.datetime")
def test_log(mock_datetime, mock_sensor, mock_controller):
    mock_sensor.value = 10
    mock_controller.value = 0
    t = datetime.datetime.now()
    mock_datetime.datetime.now.return_value = t
    with mock.patch("main.open", mock.mock_open()) as mock_open:
        main.log(mock_sensor, mock_controller)

        mock_open().write.assert_called_with(f"{t},10,0\n")


@mock.patch("main.loop", autospec=True)
@mock.patch(
    "sensors.ds18b20.DS18B20._check_device_exists",
    new=mock.MagicMock(return_value=True),
)
def test_main(mock_loop):
    main.main()
