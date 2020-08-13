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
    def set_PWM_dutycycle(self, pin, pwm):
        self._pwm = pwm

    def get_PWM_dutycycle(self, pin):
        return self._pwm


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


def test_fan_controller(fc):
    fc.setpoint = 60
    fc._humidity_sensor.value = fc.setpoint
    fc.control()

    assert fc.value == 0

    fc._humidity_sensor.value = 80
    fc.control()
    assert fc.value > 0

    fc._humidity_sensor.value = 40
    fc.control()
    assert fc.value == 0


def test_set(fc):
    fc.set(100)
