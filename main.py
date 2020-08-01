import datetime
import time
import logging

import sensors
import controllers
import wiringpi
import typing
import collections
import typing
import bme280
import smbus2

LOG = logging.getLogger(__name__)

CONTROL_INTERVAL = 10
LOG_INTERVAL = 300

wiringpi.wiringPiSetupPhys()  # use physical pin mapping

timers: typing.Dict[str, datetime.datetime] = collections.defaultdict(
    datetime.datetime.now
)


def main() -> None:
    t_bme280 = sensors.BME280_T(
        name="t_bme280", bme280_device=bme280.BME280(smbus2.SMBus(1))
    )
    heater_controller = controllers.HeaterController(control_pin=11, sensor=t_bme280)
    heater_controller.setpoint = 18

    loop(process, controllers=[heater_controller])


def loop(function: typing.Callable, *args, **kwargs) -> None:
    while True:
        function(*args, **kwargs)
        time.sleep(CONTROL_INTERVAL)


def process(
    sensors: typing.List[sensors.BaseSensor],
    controllers: typing.List[controllers.BaseController],
) -> None:
    for sensor in sensors:
        sensor.update()

    for controller in controllers:
        controller.control()

    if (datetime.datetime.now() - timers["log"]).seconds > LOG_INTERVAL:
        timers["log"] = datetime.datetime.now()
        log(*sensors, *controllers)


def log(*args) -> None:
    LOG.info("Writing log output...")
    entry = f"{datetime.datetime.now()},{','.join(str(x.value) for x in args)}"

    with open("/home/pi/gardenpi.csv", "a") as f:
        f.write(entry + "\n")


if __name__ == "__main__":
    LOG.info("Starting GardenPi")
    main()
