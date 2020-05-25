def get_temperature_from_id(sensor_id: str):
    file = f"/sys/bus/w1/devices/28-00000{sensor_id}/w1_slave"

    with open(file, 'r') as f:
        contents = f.read()
        start_pos = contents.find("t=")

        if start_pos < 0:
            return None

        return float(contents[start_pos + 2:-1]) / 1000