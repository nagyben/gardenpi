from controllers.fan_controller import FanController
import pytest
import unittest.mock as mock


@pytest.fixture
def humidity():
    return mock.MagicMock()


@pytest.fixture
def temperature():
    return mock.MagicMock()


@pytest.fixture
def pigpio():
    return mock.MagicMock()


def test_fan_controller(humidity, temperature, pigpio):
    fc = FanController(
        name="fan", humidity_sensor=humidity, temperature_sensor=temperature, pi=pigpio
    )

    fc.control()

    assert fc.value == 0
