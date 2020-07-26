import logging
import wiringpi
import sensors
import enum

LOG = logging.getLogger(__name__)


class BaseController:
    _setpoint: float
    _hysteresis: float

    def __init__(self):
        self._setpoint = 0.0
        self._hysteresis = 0.0
        self._state = None

    @property
    def setpoint(self) -> float:
        return self._setpoint

    @setpoint.setter
    def setpoint(self, setpoint: float):
        self._setpoint = setpoint

    def control(self):
        raise NotImplementedError("subclass must override control()")

    @property
    def hysteresis(self) -> float:
        return self._hysteresis

    @hysteresis.setter
    def hysteresis(self, hystersis):
        self._hysteresis = hystersis


class HeaterController(BaseController):
    class State(enum.Enum):
        COOLING = 0
        HEATING = 1

    _state: State

    def __init__(self, control_pin: int):
        if 1 <= control_pin <= 40:
            self._control_pin = control_pin
            # set control pin as output
            wiringpi.pinMode(self._control_pin, wiringpi.OUTPUT)
            # set pulldown resistor
            wiringpi.pullUpDnControl(self._control_pin, wiringpi.PUD_DOWN)
            self._state = HeaterController.State.COOLING
        else:
            raise ValueError("Control pin must be an integer in the range [0, 40]")

        return super().__init__()

    def control(self):
        temp = sensors.get_temperature_from_id(sensor_id="4cdf645")
        target_point = None
        print(f"state: {self._state}")
        if self._state == HeaterController.State.COOLING:
            target_point = self._setpoint - 0.5 * self._hysteresis
        else:
            target_point = self._setpoint + 0.5 * self._hysteresis

        print(target_point)

        if temp < target_point:
            wiringpi.digitalWrite(self._control_pin, wiringpi.HIGH)
            self._state = HeaterController.State.HEATING

        if temp >= target_point:
            wiringpi.digitalWrite(self._control_pin, wiringpi.LOW)
            self._state = HeaterController.State.COOLING
