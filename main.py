import datetime
import mcp
import time
import traceback
import logging

logging.basicConfig(level=logging.DEBUG, format="[{asctime}] {levelname} - {message}", style="{")
LOG = logging.getLogger(__name__)

def get_temperature_from_id(sensor_id: str):
    file = f"/sys/bus/w1/devices/28-00000{sensor_id}/w1_slave"

    with open(file, 'r') as f:
        contents = f.read()
        start_pos = contents.find("t=")

        if start_pos < 0:
            return None

        return float(contents[start_pos + 2:-1]) / 1000

def get_cpu_temp():
    file = "/sys/class/thermal/thermal_zone0/temp"
    with open(file, "r") as f:
        contents = f.read()
        return float(contents) / 1000


def get_lux():
    NUM_LUX_SAMPLES = 5

    lux_samples = []

    for _ in range(NUM_LUX_SAMPLES):
        lux_samples.append(mcp.readmcp())
        time.sleep(0.1)

    return sum(lux_samples) / len(lux_samples)


def main():
    sensors = ["4cba936","4cdf645","4ce8778"]
    while True:
        try:
            temps = []
            for sensor in sensors:
                temp = get_temperature_from_id(sensor)
                temps.append(temp)

            lux = get_lux()

            cpu_temp = get_cpu_temp()

            entry = f"{datetime.datetime.now()},{lux},{','.join(str(x) for x in temps)},{cpu_temp}"

            with open("/home/pi/gardenpi.csv", "a") as f:
                f.write(entry + "\n")

            time.sleep(60)
        except Exception as e:
            LOG.exception(e)

if __name__ == "__main__":
    LOG.info("Starting GardenPi")
    main()

