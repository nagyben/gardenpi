import datetime
import time
import logging

import sensors
import controllers
import wiringpi
import typing
import collections

logging.basicConfig(
    level=logging.DEBUG, format="[{asctime}] {levelname} - {message}", style="{"
)
LOG = logging.getLogger(__name__)

CONTROL_INTERVAL = 10
LOG_INTERVAL = 300

wiringpi.wiringPiSetupPhys()  # use physical pin mapping

timers: typing.Dict[str, datetime.datetime] = collections.defaultdict(
    datetime.datetime.now
)


def main():
    heater_controller = controllers.HeaterController(control_pin=11)

    main_loop(controllers=[heater_controller])


def main_loop(controllers: typing.List[controllers.BaseController]) -> None:
    while True:
        try:
            temps = sensors.get_all_temperatures()

            lux = sensors.get_lux()

            moisture = sensors.get_moisture()

            cpu_temp = sensors.get_cpu_temp()

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
        except Exception as e:
            LOG.exception(e)


def log(*args) -> None:
    entry = f"{datetime.datetime.now()},{','.join(str(x) for x in args)}"

    with open("/home/pi/gardenpi.csv", "a") as f:
        f.write(entry + "\n")


if __name__ == "__main__":
    LOG.info("Starting GardenPi")
    main()
