import datetime
import time
import logging

import sensors

logging.basicConfig(
    level=logging.DEBUG, format="[{asctime}] {levelname} - {message}", style="{"
)
LOG = logging.getLogger(__name__)


def main():
    sensors = ["4cba936", "4cdf645", "4ce8778"]
    while True:
        try:
            temps = []
            for sensor in sensors:
                temp = sensors.get_temperature_from_id(sensor)
                temps.append(temp)

            lux = sensors.get_lux()

            moisture = sensors.get_moisture()

            cpu_temp = sensors.get_cpu_temp()

            entry = f"{datetime.datetime.now()},{lux},{','.join(str(x) for x in temps)},{cpu_temp},{moisture}"

            with open("/home/pi/gardenpi.csv", "a") as f:
                f.write(entry + "\n")

            time.sleep(60)
        except Exception as e:
            LOG.exception(e)


if __name__ == "__main__":
    LOG.info("Starting GardenPi")
    main()
