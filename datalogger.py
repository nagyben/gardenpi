import collections
import concurrent.futures
import os
import queue
from typing import List, Optional

import pymongo

import sensors
import controllers
import datetime
import logging

LOG = logging.getLogger(__name__)

LOG_BATCH_SIZE = 10
MONGO_URL = os.environ.get("MONGO_URL", "localhost")

class MongoDataLogger:
    def __init__(self):
        self._log_queue = queue.Queue()
        self._log_calls = 0
        LOG.info(f"Using {MONGO_URL} as datalogger URI")

    def log(
        self,
        sensors: Optional[List[sensors.BaseSensor]],
        controllers: Optional[List[controllers.BaseController]],
    ):
        self._log_calls += 1

        def ddict():
            return collections.defaultdict(ddict)

        log_entry = ddict()

        for item in controllers:
            log_entry["controllers"][item.name]["value"] = item.value

        for item in sensors:
            log_entry["sensors"][item.name]["value"] = item.value

        log_entry["timestamp"] = datetime.datetime.now()

        self._log_queue.put(log_entry)

        if self._log_calls == LOG_BATCH_SIZE:
            self._log_calls = 0
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            executor.submit(self._log_to_mongo, self._log_queue)

    def _log_to_mongo(self, q: queue.Queue):
        client = pymongo.MongoClient(MONGO_URL)

        log_items = []

        while True:
            try:
                log_items.append(q.get_nowait())
            except queue.Empty:
                break

        if len(log_items) > 0:
            LOG.debug(f"Inserting {len(log_items)} entries to db...")
            print(client.greenhouse.data.insert_many(log_items).inserted_ids)

        else:
            LOG.warning("No items to insert into db!")
