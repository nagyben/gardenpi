from controllers.base_controller import BaseController
from sensors.base_sensor import BaseSensor
import pigpio
import logging
from simple_pid import PID

LOG = logging.getLogger(__name__)


class FanController(BaseController):
    _humidity_sensor: BaseSensor
    _temperature_sensor: BaseSensor
    _auto: bool = True
    _setpoint_temp: float

    def __init__(
        self,
        name: str,
        control_pin: int,
        humidity_sensor: BaseSensor,
        temperature_sensor: BaseSensor,
        pi,
    ):
        self._control_pin = control_pin
        self._humidity_sensor = humidity_sensor
        self._temperature_sensor = temperature_sensor
        self._pid_h = PID(-10, 0.05, 0, setpoint=0)
        self._pid_h.output_limits = (0, 100)
        self._pid_t = PID(-10, 0.05, 0, setpoint=0)
        self._pid_t.output_limits = (0, 100)
        self._pi = pi
        self._pi.set_mode(self._control_pin, pigpio.OUTPUT)
        self._pi.set_PWM_frequency(self._control_pin, 25_000)
        self.set(0)
        super().__init__(name)

    def control(self) -> None:
        if self._auto:
            # do control things
            # simple proportional PID controller

            self._pid_t.setpoint = self._setpoint_temp
            self._pid_h.setpoint = self._setpoint

            fan_duty_t = self._pid_t(self._temperature_sensor.value)
            fan_duty_h = self._pid_t(self._humidity_sensor.value)

            fan_duty = max(fan_duty_t, fan_duty_h)

            LOG.debug(f"Fan duty: {fan_duty}")

            self.set(fan_duty)

    def set(self, percent: int) -> None:
        percent = max(0, min(100, percent))
        self._pi.set_PWM_dutycycle(self._control_pin, int(percent * 255 / 100))

    @property
    def value(self) -> int:
        return int(self._pi.get_PWM_dutycycle(self._control_pin) * 100 / 255)

    @property
    def setpoint_temp(self) -> float:
        return self._setpoint_temp

    @setpoint_temp.setter
    def setpoint_temp(self, setpoint: float) -> None:
        self._setpoint_temp = setpoint
