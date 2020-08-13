import logging
import wiringpi
import sensors
import enum
from controllers.base_controller import BaseController
from sensors.base_sensor import BaseSensor

LOG = logging.getLogger(__name__)


class HeaterController(BaseController):
    class State(enum.Enum):
        COOLING = 0
        HEATING = 1

    _state: State
    _sensor: BaseSensor

    def __init__(self, name: str, control_pin: int, sensor: BaseSensor):
        if 1 <= control_pin <= 40:
            self._control_pin = control_pin
            # set control pin as output
            wiringpi.pinMode(self._control_pin, wiringpi.OUTPUT)
            # set pulldown resistor
            wiringpi.pullUpDnControl(self._control_pin, wiringpi.PUD_DOWN)
            self._state = HeaterController.State.COOLING
        else:
            raise ValueError("Control pin must be an integer in the range [0, 40]")

        self._sensor = sensor
        super().__init__(name)

    def control(self):
        temp = self._sensor.value
        target_point = None
        LOG.debug(f"{self} state: {self._state}")
        if self._state == HeaterController.State.COOLING:
            target_point = self._setpoint - 0.5 * self._hysteresis
        else:
            target_point = self._setpoint + 0.5 * self._hysteresis

        if temp < target_point:
            wiringpi.digitalWrite(self._control_pin, wiringpi.HIGH)
            self._state = HeaterController.State.HEATING

        if temp >= target_point:
            wiringpi.digitalWrite(self._control_pin, wiringpi.LOW)
            self._state = HeaterController.State.COOLING

    def state(self) -> int:
        return self._state.value

    @property
    def value(self):
        return self.state()
