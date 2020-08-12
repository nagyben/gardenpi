from controllers.base_controller import BaseController
from sensors.base_sensor import BaseSensor
import time

SERVO_OPEN = 2400
SERVO_CLOSED = 1500
SERVO_TIME_STEP = 0.05


class VentController(BaseController):
    _temp_sensor: BaseSensor
    _humidity_sensor: BaseSensor
    _position: int = SERVO_OPEN

    def __init__(
        self, name: str, control_pin: int, fan_controller: BaseController, pi,
    ):
        self._control_pin = control_pin
        self._fan_controller = fan_controller
        self._pi = pi

        self._pi.set_servo_pulsewidth(self._control_pin, self._position)

        super().__init__(name)

    def control(self) -> None:
        # TODO: make better rules
        # if fan is on then open vent
        # if fan is off then close vent
        if self._fan_controller.value > 0:
            if self.value < 100:
                self.open_vent()

        if self._fan_controller.value == 0:
            if self.value > 0:
                self.close_vent()

    def open_vent(self, time_to_open: float = 1) -> None:
        self._move_vent_to_position(SERVO_OPEN, time_to_open)

    def close_vent(self, time_to_open: float = 1) -> None:
        self._move_vent_to_position(SERVO_CLOSED, time_to_open)

    def _move_vent_to_position(self, target_position: int, time_to_open: float) -> None:
        movement = target_position - self._position
        step = movement / time_to_open * SERVO_TIME_STEP
        print(f"step: {step}")

        while self._position != target_position:
            new_pos = self._pi.get_servo_pulsewidth(self._control_pin) + step
            self._pi.set_servo_pulsewidth(self._control_pin, new_pos)
            self._position = new_pos
            print(f"_position: {self._position}")
            time.sleep(SERVO_TIME_STEP)

    @property
    def value(self):
        return (self._position - SERVO_CLOSED) / (SERVO_OPEN - SERVO_CLOSED) * 100
