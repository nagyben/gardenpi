from controllers.base_controller import BaseController
from sensors.base_sensor import BaseSensor
import pigpio


class FanController(BaseController):
    _humidity_sensor: BaseSensor
    _temperature_sensor: BaseSensor
    _auto: bool = True

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
        self._pi = pi
        self._kp = -10
        self._pi.set_mode(self._control_pin, pigpio.OUTPUT)
        self._pi.set_PWM_frequency(self._control_pin, 25_000)
        self.set(0)
        super().__init__(name)

    def control(self) -> None:
        if self._auto:
            # do control things
            # simple proportional PID controller

            # calculate error between setpoint and humidity sensor
            error = self._setpoint - self._humidity_sensor.value

            fan_duty = self._kp * error

            self.set(fan_duty)

    def set(self, percent: int) -> None:
        percent = max(0, min(100, percent))
        self._pi.set_PWM_dutycycle(self._control_pin, int(percent * 255 / 100))

    @property
    def value(self) -> int:
        return int(self._pi.get_PWM_dutycycle(self._control_pin) * 100 / 255)
