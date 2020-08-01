import datetime
import time
import logging

import sensors
import controllers
import wiringpi
import typing
import collections

LOG = logging.getLogger(__name__)

CONTROL_INTERVAL = 10
LOG_INTERVAL = 300

wiringpi.wiringPiSetupPhys()  # use physical pin mapping

timers: typing.Dict[str, datetime.datetime] = collections.defaultdict(
    datetime.datetime.now
)


def main() -> None:

    heater_controller = controllers.HeaterController(control_pin=11)
    heater_controller.setpoint = 18

    loop(process, controllers=[heater_controller])


def loop(function: callable, *args, **kwargs) -> None:
    while True:
        function(*args, **kwargs)


def process(
    sensors: typing.List[sensors.BaseSensor],
    controllers: typing.List[controllers.BaseController],
) -> None:

    for controller in controllers:
        controller.control()

    if (datetime.datetime.now() - timers["log"]).seconds > LOG_INTERVAL:
        timers["log"] = datetime.datetime.now()
        log(
            lux,
            *[temps[key] for key in temps.keys()],
            cpu_temp,
            moisture,
            *[controller.state() for controller in controllers],
        )

    time.sleep(CONTROL_INTERVAL)


def log(*args) -> None:
    LOG.info("Writing log output...")
    entry = f"{datetime.datetime.now()},{','.join(str(x) for x in args)}"

    with open("/home/pi/gardenpi.csv", "a") as f:
        f.write(entry + "\n")


if __name__ == "__main__":
    LOG.info("Starting GardenPi")
    main()
