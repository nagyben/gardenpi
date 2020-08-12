from controllers.base_controller import BaseController
from controllers.vent_controller import VentController
from sensors.base_sensor import BaseSensor
import unittest.mock as mock
import pytest


@pytest.fixture
def fan_controller():
    return mock.MagicMock(spec=BaseController)


class MockPiGPIO:
    _pulsewidth: int

    def __init__(self):
        self._pulsewidth = 0

    def set_servo_pulsewidth(self, pin, pw) -> int:
        self._pulsewidth = pw
        return pw

    def get_servo_pulsewidth(self, pin) -> int:
        return self._pulsewidth


@mock.patch("time.sleep", new=lambda x: x)
def test_vent_controller(fan_controller):
    vc = VentController(
        name="vent", control_pin=1, fan_controller=fan_controller, pi=MockPiGPIO(),
    )

    fan_controller.value = 0
    vc.control()

    assert vc.value == 0

    fan_controller.value = 1

    vc.control()

    assert vc.value == 100
