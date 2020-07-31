class BaseSensor:
    name: str

    def __init__(self, name: str):
        self.name = name

    def value(self):
        raise NotImplementedError("subclass must override value()")
