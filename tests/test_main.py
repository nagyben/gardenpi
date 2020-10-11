import sys
import unittest.mock as mock
import main
import sensors.base_sensor
import controllers.base_controller
import pytest
import datetime
import queue
import mongomock

@pytest.fixture
def mock_sensor():
    return mock.MagicMock(spec=sensors.base_sensor.BaseSensor)


@pytest.fixture
def mock_controller():
    return mock.MagicMock(spec=controllers.base_controller.BaseController)


@mock.patch("main.open", new=mock.MagicMock())
def test_process(mock_sensor, mock_controller):
    mock_sensor.value = 10
    mock_controller.value = 0
    main.process(sensors=[mock_sensor], controllers=[mock_controller])


@mock.patch("concurrent.futures.ThreadPoolExecutor")
@mock.patch("main.log_to_mongo")
@mock.patch("main.datetime")
def test_log(mock_datetime, log_to_mongo, mock_threads, mock_sensor, mock_controller):
    mock_sensor.value = 10
    mock_sensor.name = "sensor"
    mock_controller.value = 0
    mock_controller.name = "controller"

    times = []
    q = queue.Queue()
    for _ in range(10):
        times.append(datetime.datetime.now())
        mock_datetime.datetime.now.return_value = times[-1]
        main.log(mock_sensor, mock_controller)
        q.put({
                "timestamp": times[-1],
                "controllers": {"controller": {"value": 0}},
                "sensors": {"sensor": {"value": 10}},
            })

    mock_threads.submit.assert_called_with(main.log_to_mongo, q)

@mongomock.patch(on_new="create")
def test_log_to_mongo():
    times = range(10)
    q = queue.Queue()

    [q.put({
                "timestamp": t,
                "controllers": {"controller": {"value": 0}},
                "sensors": {"sensor": {"value": 10}},
            }) for t in times]

    main.log_to_mongo(q)

    inserts = mongomock.MongoClient().greenhouse.data.find({})

    for i, insert in enumerate(inserts):
        assert insert["timestamp"] == times[i]



@mock.patch(
    "sensors.ds18b20.DS18B20._check_device_exists",
    new=mock.MagicMock(return_value=True),
)
@mock.patch("main.atexit")
@mock.patch("main.Loop")
@mock.patch("main.process")
def test_main(process, loop, atexit):
    main.main()

    loop.return_value.start.assert_called_once()
    atexit.register.assert_called_once()
