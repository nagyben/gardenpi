import main
import unittest.mock as mock
import sensors.base_sensor


def test_process():
    main.process(sensors=[], controllers=[])
