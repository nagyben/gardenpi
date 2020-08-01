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

    def state(self):
        raise NotImplementedError("subclass must override state()")

    @property
    def value(self):
        raise NotImplementedError("subclass must override property value")
