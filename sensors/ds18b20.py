from sensors.base_sensor import BaseSensor
import pathlib
import numpy


class DS18B20(BaseSensor):
    _id: str
    _device_path: str

    def __init__(self, name: str, id: str):
        if not self._check_device_exists(id):
            raise IOError(
                f"Sensor with id {id} could not be found. Make sure it is connected"
            )

        self._id = id
        self._device_path = f"/sys/bus/w1/devices/28-00000{id}/w1_slave"
        super().__init__(name)

    @property
    def value(self):
        return self._value

    def update(self):
        with open(self._device_path, "r") as f:
            contents = f.read()
            start_pos = contents.find("t=")

            if start_pos < 0:
                self._value = numpy.nan

            else:
                self._value = float(contents[start_pos + 2 : -1]) / 1000

    def _check_device_exists(self, id: str) -> bool:
        return pathlib.Path(f"/sys/bus/w1/devices/28-00000{id}/w1_slave").exists()
