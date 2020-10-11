import datalogger

def test_datalogger():
    dl = datalogger.DataLogger()

    dl.log()

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
    for _ in range(main.LOG_BATCH_SIZE):
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