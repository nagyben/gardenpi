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
import queue
import pymongo
import os
import concurrent.futures

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

LOG_QUEUE = queue.Queue()
LOG_BATCH_SIZE = 10

MONGO_URL = os.environ.get("MONGO_URL")
MONGO_USERNAME = os.environ.get("MONGO_USERNAME")
MONGO_PASSWORD = os.environ.get("MONGO_PASSWORD")

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
    bme280_device = bme280.BME280(i2c_dev=smbus2.SMBus(1))
    t_bme280 = sensors.BME280_T(name="t_bme280", bme280_device=bme280_device)
    pressure = sensors.BME280_P(name="pressure", bme280_device=bme280_device)
    humidity = sensors.BME280_H(name="humidity", bme280_device=bme280_device)

    LOG.info("Stabilizing BME280...")
    for i in range(3):
        for sensor in [t_bme280, pressure, humidity]:
            sensor.update()

        LOG.info(
            f"{' '.join(str(sensor.value) for sensor in [t_bme280, pressure, humidity])}"
        )
        time.sleep(1)

    LOG.info("Setting up ambient light sensor...")
    SPI = Adafruit_GPIO.SPI.SpiDev(SPI_PORT, SPI_DEVICE)
    ambient_light = sensors.MCPSensor(
        name="ambient_light",
        mcp3xxx=Adafruit_MCP3008.MCP3008(
            spi=SPI
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
        name="heater", control_pin=11, sensor=t_bme280
    )
    heater_controller.setpoint = 18

    LOG.info("Setting up pigpio")
    pi = pigpio.pi()

    LOG.info("Setting up fan controller...")
    fan_controller = controllers.FanController(
        name="fan",
        control_pin=15,
        humidity_sensor=humidity,
        temperature_sensor=t_bme280,
        pi=pi,
    )

    fan_controller.setpoint = 60
    fan_controller.setpoint_temp = 20

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
        sensors=[*t_ds18b20, t_bme280, pressure, humidity, ambient_light],
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
    def ddict():
        return collections.defaultdict(ddict)

    log_entry = ddict()

    for _ in range(LOG_BATCH_SIZE):
        for item in args:
            if isinstance(item, controllers.BaseController):
                log_entry["controllers"][item.name]["value"] = item.value

            if isinstance(item, sensors.BaseSensor):
                log_entry["sensors"][item.name]["value"] = item.value


        log_entry["timestamp"] = datetime.datetime.now()

        LOG_QUEUE.put(log_entry)

        print("herp")

        yield

    print(LOG_QUEUE.qsize())

    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    executor.submit(log_to_mongo, LOG_QUEUE)



def log_to_mongo(q: queue.Queue):
    client = pymongo.MongoClient(f"mongodb+srv://{MONGO_USERNAME}{MONGO_PASSWORD}@{MONGO_URL}/garden?retryWrites=true&w=majority")

    log_items = []

    while True:
        try:
            log_items.append(q.get_nowait())
        except queue.Empty:
            break

    if len(log_items) > 0:
        LOG.debug(f"Inserting {len(log_items)} entries to db...")
        client.garden["greenhouse-data"].insert_many(log_items)

    else:
        LOG.warning("No items to insert into db!")


if __name__ == "__main__":
    LOG.info("Starting GardenPi")
    main()
