import datetime
import time
import logging

import sensors
import controllers
import wiringpi
import typing

logging.basicConfig(
    level=logging.DEBUG, format="[{asctime}] {levelname} - {message}", style="{"
)
LOG = logging.getLogger(__name__)

SENSOR_INTERVAL = 300

wiringpi.wiringPiSetupPhys()  # use physical pin mapping


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

            entry = f"{datetime.datetime.now()},{lux},{','.join(str(temps[key]) for key in temps.keys())},{cpu_temp},{moisture}"

            with open("/home/pi/gardenpi.csv", "a") as f:
                f.write(entry + "\n")

            time.sleep(SENSOR_INTERVAL)
        except Exception as e:
            LOG.exception(e)


if __name__ == "__main__":
    LOG.info("Starting GardenPi")
    main()
