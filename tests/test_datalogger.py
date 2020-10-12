import datetime
import unittest.mock as mock
import mongomock
import pymongo

import sensors
import datalogger
import pytest
import queue


@pytest.fixture
def mock_sensor():
    return mock.MagicMock(autospec=sensors.BaseSensor)


@pytest.fixture
def mock_controller():
    return mock.MagicMock(autospec=sensors.BaseSensor)


def test_init():
    dl = datalogger.MongoDataLogger()
    assert isinstance(dl._log_queue, queue.Queue)


@mock.patch("concurrent.futures.ThreadPoolExecutor")
@mock.patch("datalogger.datetime")
def test_datalogger(mock_datetime, mock_threadpool):
    dl = datalogger.MongoDataLogger()
    mock_sensor.value = 10
    mock_sensor.name = "sensor"
    mock_controller.value = 0
    mock_controller.name = "controller"

    times = []
    q = queue.Queue()
    dl._log_queue = q
    for _ in range(datalogger.LOG_BATCH_SIZE):
        times.append(datetime.datetime.now())
        mock_datetime.datetime.now.return_value = times[-1]
        dl.log(sensors=[mock_sensor], controllers=[mock_controller])
        q.put(
            {
                "timestamp": times[-1],
                "controllers": {"controller": {"value": 0}},
                "sensors": {"sensor": {"value": 10}},
            }
        )

    mock_threadpool.return_value.submit.assert_called_with(dl._log_to_mongo, q)


@mongomock.patch(on_new="create")
def test_log_to_mongo():
    dl = datalogger.MongoDataLogger()
    times = range(10)
    q = queue.Queue()

    [
        q.put(
            {
                "timestamp": t,
                "controllers": {"controller": {"value": 0}},
                "sensors": {"sensor": {"value": 10}},
            }
        )
        for t in times
    ]

    dl._log_to_mongo(q)

    inserts = list(pymongo.MongoClient(datalogger.MONGO_URL).greenhouse.data.find())

    assert len(inserts) == 10
    for i, insert in enumerate(inserts):
        assert insert["timestamp"] == times[i]
