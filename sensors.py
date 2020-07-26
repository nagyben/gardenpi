import time
import numpy

import mcp

MCP_CHANNELS = {"lux": 0, "moisture": 6}

EXTERNAL_TEMPERATURE_SENSOR_IDS = ["4cba936"]

INTERNAL_TEMPERATURE_SENSOR_IDS = ["4cdf645", "4ce8778"]


def get_temperature_from_id(sensor_id: str) -> float:
    file = f"/sys/bus/w1/devices/28-00000{sensor_id}/w1_slave"

    with open(file, "r") as f:
        contents = f.read()
        start_pos = contents.find("t=")

        if start_pos < 0:
            return numpy.nan

        return float(contents[start_pos + 2 : -1]) / 1000


def get_cpu_temp() -> float:
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
