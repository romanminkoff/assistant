import datetime
import multiprocessing
import os
import time

from assistant import assistant
from assistant.scheduler import Schedule


def test_message_broker():
    multiprocessing.current_process()._tmp_msg_received = False
    def _msg_from_broker(_):
        multiprocessing.current_process()._tmp_msg_received = True

    a = assistant.Assistant(msg_from_broker=_msg_from_broker)
    t = datetime.datetime.now() + datetime.timedelta(seconds=2)
    t1 = t.time()
    cwd = os.path.dirname(__file__)
    a.add_job("J", os.path.join(cwd, "example_job.py"),
              params=None, is_active=True)
    a.reschedule_job("J", Schedule(t1, "daily"))
    time.sleep(1)
    assert multiprocessing.current_process()._tmp_msg_received == False
    time.sleep(2)
    assert multiprocessing.current_process()._tmp_msg_received == True
