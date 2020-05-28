import datetime
def get_temperature_from_id(sensor_id: str):
    file = f"/sys/bus/w1/devices/28-00000{sensor_id}/w1_slave"

    with open(file, 'r') as f:
        contents = f.read()
        start_pos = contents.find("t=")

        if start_pos < 0:
            return None

        return float(contents[start_pos + 2:-1]) / 1000


def main():
    sensors = ["4cba936","4cdf645","4ce8778"]
    while True:
        temps = []
        for sensor in sensors:
            temp = get_temperature_from_id(sensor)
            temps.append(temp)

        print(f"{datetime.datetime.now()},{','.join(str(x) for x in temps)}")
main()

