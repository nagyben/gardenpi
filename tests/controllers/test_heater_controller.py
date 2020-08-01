from controllers import HeaterController
from sensors import BaseSensor
import unittest.mock as mock
import pytest


@pytest.fixture
def wiringpi():
    with mock.patch("controllers.heater_controller.wiringpi") as patched:
        yield patched


@pytest.mark.parametrize(
    "control_pin,raises", [(0, True), (1, False), (40, False), (41, True)]
)
def test_init_control_pins(control_pin, raises, wiringpi):
    if raises:
        with pytest.raises(ValueError):
            HeaterController(control_pin=control_pin, sensor=mock.MagicMock())

    else:
        HeaterController(control_pin=control_pin, sensor=mock.MagicMock())
        wiringpi.pinMode.assert_called_with(control_pin, wiringpi.OUTPUT)
        wiringpi.pullUpDnControl.assert_called_with(control_pin, wiringpi.PUD_DOWN)


def test_temperature_below_setpoint_and_hysteresis(wiringpi):
    mock_sensor = mock.MagicMock()
    heater_controller = HeaterController(control_pin=1, sensor=mock_sensor)
    heater_controller.setpoint = 20
    heater_controller.hysteresis = 2

    mock_sensor.value = 10
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.HIGH)


def test_temperature_above_setpoint_and_hysteresis(wiringpi):
    mock_sensor = mock.MagicMock()
    heater_controller = HeaterController(control_pin=1, sensor=mock_sensor)
    heater_controller.setpoint = 20
    heater_controller.hysteresis = 2

    mock_sensor.value = 30
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.LOW)


def test_hysteresis_upwards(wiringpi):
    mock_sensor = mock.MagicMock()
    heater_controller = HeaterController(control_pin=1, sensor=mock_sensor)
    heater_controller.setpoint = 20
    heater_controller.hysteresis = 2

    # if the temperature is below (setpoint - 0.5 * hysteresis) then we want
    # to keep heating until we reach (setpoint + 0.5 * hysteresis)
    mock_sensor.value = 18.9
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.HIGH)

    # simulate crossing lower bound
    mock_sensor.value = 19.1
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.HIGH)

    # continue past setpoint
    mock_sensor.value = 20.1
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.HIGH)

    # keep going...
    mock_sensor.value = 20.9
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.HIGH)

    # ... until we hit the upper hysteresis limit
    mock_sensor.value = 21.0
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.LOW)


def test_hysteresis_downwards(wiringpi):
    mock_sensor = mock.MagicMock()
    heater_controller = HeaterController(control_pin=1, sensor=mock_sensor)
    heater_controller.setpoint = 20
    heater_controller.hysteresis = 2

    # if the temperature is below (setpoint - 0.5 * hysteresis) then we want
    # to keep heating until we reach (setpoint + 0.5 * hysteresis)
    mock_sensor.value = 22
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.LOW)

    # simulate crossing upper bound
    mock_sensor.value = 21
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.LOW)

    # continue past setpoint
    mock_sensor.value = 20
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.LOW)

    # keep going...
    mock_sensor.value = 19.9
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.LOW)

    # ... until we hit the lower hysteresis limit
    mock_sensor.value = 18.9
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.HIGH)


def test_get_value():
    mock_sensor = mock.MagicMock()
    heater_controller = HeaterController(control_pin=1, sensor=mock_sensor)
    heater_controller.setpoint = 20
    heater_controller.hysteresis = 2

    mock_sensor.value = 22
    heater_controller.control()
    assert heater_controller.value == 0
