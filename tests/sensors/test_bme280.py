from sensors import BME280_T, BME280_P, BME280_H
import pytest
import numpy
import unittest.mock as mock


def test_bme280_temperature():
    bme280_device = mock.MagicMock()
    bme280_device.get_temperature.return_value = 1
    b = BME280_T(name="temp_bme280", bme280_device=bme280_device)

    assert b.value == 0

    b.update()
    assert b.value == 1


def test_bme280_humidity():
    bme280_device = mock.MagicMock()
    bme280_device.get_humidity.return_value = 1
    b = BME280_H(name="humidity", bme280_device=bme280_device)

    assert b.value == 0

    b.update()
    assert b.value == 1


def test_bme280_pressure():
    bme280_device = mock.MagicMock()
    bme280_device.get_pressure.return_value = 1
    b = BME280_P(name="pressure", bme280_device=bme280_device)

    assert b.value == 0

    b.update()
    assert b.value == 1
