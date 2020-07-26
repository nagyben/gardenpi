import controllers
import unittest.mock as mock
import pytest


@pytest.fixture
def wiringpi():
    with mock.patch("controllers.wiringpi") as patched:
        yield patched


@pytest.fixture
def sensors():
    with mock.patch("controllers.sensors") as patched:
        yield patched


@pytest.mark.parametrize(
    "control_pin,raises", [(0, True), (1, False), (40, False), (41, True)]
)
def test_init_control_pins(control_pin, raises, wiringpi):
    if raises:
        with pytest.raises(ValueError):
            controllers.HeaterController(control_pin=control_pin)

    else:
        controllers.HeaterController(control_pin=control_pin)
        wiringpi.pinMode.assert_called_with(control_pin, wiringpi.OUTPUT)
        wiringpi.pullUpDnControl.assert_called_with(control_pin, wiringpi.PUD_DOWN)


def test_temperature_below_setpoint_and_hysteresis(sensors, wiringpi):
    heater_controller = controllers.HeaterController(control_pin=1)
    heater_controller.setpoint = 20
    heater_controller.hysteresis = 2

    controllers.sensors.get_temperature_from_id.return_value = 10
    heater_controller.control()
    sensors.get_temperature_from_id.assert_called_with(sensor_id="4cdf645")
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.HIGH)


def test_temperature_above_setpoint_and_hysteresis(sensors, wiringpi):
    heater_controller = controllers.HeaterController(control_pin=1)
    heater_controller.setpoint = 20
    heater_controller.hysteresis = 2

    controllers.sensors.get_temperature_from_id.return_value = 30
    heater_controller.control()
    sensors.get_temperature_from_id.assert_called_with(sensor_id="4cdf645")
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.LOW)


def test_hysteresis_upwards(sensors, wiringpi):
    heater_controller = controllers.HeaterController(control_pin=1)
    heater_controller.setpoint = 20
    heater_controller.hysteresis = 2

    # if the temperature is below (setpoint - 0.5 * hysteresis) then we want
    # to keep heating until we reach (setpoint + 0.5 * hysteresis)
    controllers.sensors.get_temperature_from_id.return_value = 18.9
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.HIGH)

    # simulate crossing lower bound
    controllers.sensors.get_temperature_from_id.return_value = 19.1
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.HIGH)

    # continue past setpoint
    controllers.sensors.get_temperature_from_id.return_value = 20.1
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.HIGH)

    # keep going...
    controllers.sensors.get_temperature_from_id.return_value = 20.9
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.HIGH)

    # ... until we hit the upper hysteresis limit
    controllers.sensors.get_temperature_from_id.return_value = 21.0
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.LOW)


def test_hysteresis_downwards(sensors, wiringpi):
    heater_controller = controllers.HeaterController(control_pin=1)
    heater_controller.setpoint = 20
    heater_controller.hysteresis = 2

    # if the temperature is below (setpoint - 0.5 * hysteresis) then we want
    # to keep heating until we reach (setpoint + 0.5 * hysteresis)
    controllers.sensors.get_temperature_from_id.return_value = 22
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.LOW)

    # simulate crossing upper bound
    controllers.sensors.get_temperature_from_id.return_value = 21
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.LOW)

    # continue past setpoint
    controllers.sensors.get_temperature_from_id.return_value = 20
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.LOW)

    # keep going...
    controllers.sensors.get_temperature_from_id.return_value = 19.9
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.LOW)

    # ... until we hit the lower hysteresis limit
    controllers.sensors.get_temperature_from_id.return_value = 18.9
    heater_controller.control()
    wiringpi.digitalWrite.assert_called_with(1, wiringpi.HIGH)
