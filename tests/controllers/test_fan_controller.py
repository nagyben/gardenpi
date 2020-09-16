from controllers.fan_controller import FanController
import pytest
import unittest.mock as mock


@pytest.fixture
def humidity():
    return mock.MagicMock()


@pytest.fixture
def temperature():
    return mock.MagicMock()


class MockPi:
    def __init__(self):
        self.set_PWM_dutycycle = mock.MagicMock(side_effect=self.setpwm)

    def setpwm(self, pin, pwm):
        self._pwm = pwm

    def get_PWM_dutycycle(self, pin):
        return self._pwm

    set_PWM_frequency = mock.MagicMock()
    set_mode = mock.MagicMock()


@pytest.fixture
def pi():
    return MockPi()


@pytest.fixture
def fc(humidity, temperature, pi):
    return FanController(
        name="fan",
        control_pin=1,
        humidity_sensor=humidity,
        temperature_sensor=temperature,
        pi=pi,
    )


def test_fan_controller_init(humidity, temperature, pi):
    FanController(
        name="fan",
        control_pin=1,
        humidity_sensor=humidity,
        temperature_sensor=temperature,
        pi=pi,
    )

    pi.set_PWM_frequency.assert_called_with(1, 25_000)
    pi.set_PWM_dutycycle.assert_called_with(1, 0)
    pi.set_mode.assert_called_once()


def test_fan_controller(fc):
    fc.setpoint = 60
    fc.setpoint_temp = 25
    fc._humidity_sensor.value = fc.setpoint
    fc._temperature_sensor.value = 20
    fc.control()

    assert fc.value == 0

    fc._temperature_sensor.value = 30
    fc.control()

    assert fc.value > 0

    fc._temperature_sensor.value = 20
    fc._humidity_sensor.value = 80
    fc.control()
    assert fc.value > 0


def test_set(fc):
    fc.set(100)
