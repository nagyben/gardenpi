import datetime
import time
import logging

import sensors
import controllers
import wiringpi
import typing
import collections
import bme280
import smbus2
import Adafruit_GPIO.SPI
import Adafruit_MCP3008
import pigpio
import threading
import atexit

logging.basicConfig(
    level=logging.INFO, format="[{asctime}] {levelname} - {message}", style="{"
)

LOG = logging.getLogger(__name__)

LOOP_INTERVAL = 1
LOG_INTERVAL = 120

wiringpi.wiringPiSetupPhys()  # use physical pin mapping

timers: typing.Dict[str, datetime.datetime] = collections.defaultdict(
    datetime.datetime.now
)

SPI_PORT = 0
SPI_DEVICE = 0


class Loop(threading.Thread):
    def __init__(
        self, event: threading.Event, target: typing.Callable, *args, **kwargs
    ):
        threading.Thread.__init__(self)
        self.stopped = event
        self._args = args
        self._kwargs = kwargs
        self._target = target

    def run(self):
        while not self.stopped.wait(LOOP_INTERVAL):
            self._target(*self._args, **self._kwargs)


STOP_FLAG = threading.Event()


def main() -> None:
    LOG.info("Setting up BME280...")
    i2c_dev = smbus2.SMBus(1)
    bme280_device_internal = bme280.BME280(i2c_dev=i2c_dev)
    bme280_device_external = bme280.BME280(i2c_dev=i2c_dev, i2c_addr=0x77)
    t_bme280_internal = sensors.BME280_T(
        name="t_bme280", bme280_device=bme280_device_internal
    )
    pressure_internal = sensors.BME280_P(
        name="pressure", bme280_device=bme280_device_internal
    )
    humidity_internal = sensors.BME280_H(
        name="humidity", bme280_device=bme280_device_internal
    )

    t_bme280_external = sensors.BME280_T(
        name="t_bme280_external", bme280_device=bme280_device_external
    )
    humidity_external = sensors.BME280_H(
        name="humidity_external", bme280_device=bme280_device_external
    )

    LOG.info("Stabilizing sensors...")
    stabilization_sensors = [
        t_bme280_internal,
        pressure_internal,
        humidity_internal,
        t_bme280_external,
        humidity_external,
    ]
    for i in range(3):
        for sensor in stabilization_sensors:
            sensor.update()

        LOG.info(f"{' '.join(str(sensor.value) for sensor in stabilization_sensors)}")
        time.sleep(1)

    LOG.info("Setting up ambient light sensor...")
    ambient_light = sensors.MCPSensor(
        name="ambient_light",
        mcp3xxx=Adafruit_MCP3008.MCP3008(
            spi=Adafruit_GPIO.SPI.SpiDev(SPI_PORT, SPI_DEVICE)
        ),
        channel=0,
    )

    LOG.info("Setting up DS18B20 sensors...")
    t_ds18b20 = [
        sensors.DS18B20(name="t_internal_1", id="4cba936"),
        sensors.DS18B20(name="t_external", id="4cdf645"),
        sensors.DS18B20(name="t_internal_2", id="4ce8778"),
    ]

    LOG.info("Setting up heater controller...")
    heater_controller = controllers.HeaterController(
        name="heater", control_pin=11, sensor=t_bme280_internal
    )
    heater_controller.setpoint = 18

    LOG.info("Setting up pigpio")
    pi = pigpio.pi()

    LOG.info("Setting up fan controller...")
    fan_controller = controllers.FanController(
        name="fan",
        control_pin=15,
        humidity_sensor=humidity_internal,
        temperature_sensor=t_bme280_internal,
        pi=pi,
    )

    fan_controller.setpoint = 60
    fan_controller.setpoint_temp = 20
    fan_controller.set_external_humidity_sensor(humidity_external)

    LOG.info("Setting up vent controller...")
    vent_controller = controllers.VentController(
        name="vent",
        control_pin=18,  # BCM-style control pin
        pi=pi,
        fan_controller=fan_controller,
    )

    LOG.info("Starting control loop...")
    looper = Loop(
        event=STOP_FLAG,
        target=process,
        sensors=[
            *t_ds18b20,
            t_bme280_internal,
            pressure_internal,
            humidity_internal,
            ambient_light,
            t_bme280_external,
            humidity_external,
        ],
        controllers=[heater_controller, fan_controller, vent_controller],
    )
    looper.start()

    atexit.register(on_exit, [looper])


def on_exit(threads: typing.List[threading.Thread]):
    LOG.info("Setting stop flag")
    STOP_FLAG.set()

    LOG.info("Waiting for threads to exit")
    for thread in threads:
        thread.join()

    LOG.info("Goodbye")


def process(
    sensors: typing.List[sensors.BaseSensor],
    controllers: typing.List[controllers.BaseController],
) -> None:
    LOG.debug("Updating sensors...")
    for sensor in sensors:
        sensor.update()

    LOG.debug("Updating controllers...")
    for controller in controllers:
        controller.control()

    if (datetime.datetime.now() - timers["log"]).seconds > LOG_INTERVAL:
        timers["log"] = datetime.datetime.now()
        log(*sensors, *controllers)


def log(*args) -> None:
    LOG.debug("Writing log output...")
    entry = f"{datetime.datetime.now()},{','.join(str(x.value) for x in args)}"

    with open("/home/pi/gardenpi.csv", "a") as f:
        f.write(entry + "\n")


if __name__ == "__main__":
    LOG.info("Starting GardenPi")
    main()
