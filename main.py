import datetime
import mcp
import time
import traceback
import logging

logging.basicConfig(level=logging.DEBUG, format="[{asctime}] {levelname} - {message}", style="{")
LOG = logging.getLogger(__name__)

MCP_CHANNELS = {
    "lux": 0,
    "moisture": 6
}

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


def get_lux(num_samples: int = 5) -> float:
    lux_samples = []

    for _ in range(num_samples):
        lux_samples.append(mcp.readmcp(MCP_CHANNELS["lux"]))
        time.sleep(0.1)

    return sum(lux_samples) / len(lux_samples)


def get_moisture(num_samples: int = 5) -> float:
    moisture_samples = []

    for _ in range(num_samples):
        moisture_samples.append(mcp.readmcp(MCP_CHANNELS["moisture"]))
        time.sleep(0.1)

    return sum(moisture_samples) / len(moisture_samples)


def main():
    sensors = ["4cba936","4cdf645","4ce8778"]
    while True:
        try:
            temps = []
            for sensor in sensors:
                temp = get_temperature_from_id(sensor)
                temps.append(temp)

            lux = get_lux()

            moisture = get_moisture()

            cpu_temp = get_cpu_temp()

            entry = f"{datetime.datetime.now()},{lux},{','.join(str(x) for x in temps)},{cpu_temp},{moisture}"

            with open("/home/pi/gardenpi.csv", "a") as f:
                f.write(entry + "\n")

            time.sleep(60)
        except Exception as e:
            LOG.exception(e)

if __name__ == "__main__":
    LOG.info("Starting GardenPi")
    main()

