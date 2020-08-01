import typing


class BaseSensor:
    name: str
    _value: typing.Union[int, float]

    def __init__(self, name: str):
        self.name = name
        self._value = 0

    @property
    def value(self):
        return self._value

    def update(self):
        raise NotImplementedError("subclass must override update()")
