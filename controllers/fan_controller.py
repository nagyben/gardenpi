from controllers.base_controller import BaseController
from sensors.base_sensor import BaseSensor


class FanController(BaseController):
    _humidity_sensor: BaseSensor
    _temperature_sensor: BaseSensor
    _fan_dutycycle: int = 0

    def __init__(
        self, name: str, humidity_sensor: BaseSensor, temperature_sensor: BaseSensor, pi
    ):
        self._humidity_sensor = humidity_sensor
        self._temperature_sensor = temperature_sensor
        self._pi = pi
        super().__init__(name)

    def control(self) -> None:
        pass

    @property
    def value(self) -> int:
        return int(self._fan_dutycycle / 255 * 100)
