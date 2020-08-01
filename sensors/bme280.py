from sensors.base_sensor import BaseSensor
import typing_extensions


class BME280Protocol(typing_extensions.Protocol):
    def get_temperature(self):
        ...

    def get_pressure(self):
        ...

    def get_humidity(self):
        ...


class BME280Base(BaseSensor):
    _bme280: BME280Protocol

    def __init__(self, name: str, bme280_device: BME280Protocol):
        self._bme280 = bme280_device
        super().__init__(name)


class BME280_T(BME280Base):
    def update(self):
        self._value = self._bme280.get_temperature()


class BME280_P(BME280Base):
    def update(self):
        self._value = self._bme280.get_pressure()


class BME280_H(BME280Base):
    def update(self):
        self._value = self._bme280.get_humidity()
