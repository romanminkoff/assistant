import datetime
import pytest

import assistant
import job
from schedule import Schedule, Interval, Day, ScheduleInitException

def teardown_function():
    assistant.reset()


### assistant
def test_add_job():
    assistant._add_job("A", "path", params=None, is_active=False)
    assert len(assistant.jobs) == 1
    assert "A" in assistant.jobs
    with pytest.raises(assistant.AssistantAddJobException):
        assistant._add_job("A", "path2", params=None, is_active=False)

def test_dump_jobs():
    assistant._add_job("A", "path", params=None, is_active=False)
    cfg = assistant._jobs_config_json()
    assert len(cfg["jobs"]) == 1
    assert "A" in cfg["jobs"]

def test_job_from_cfg():
    cfg = {
        "name": "A",
        "path": "path",
        "params": {
            "whatever": 5
        },
        "is_active": False,
        "schedule": [
            {
                "time": "15:34:00",
                "interval": "day",
                "interval_arg": "Friday"
            },
            {
                "time": "04:01:05",
                "interval": "daily",
                "interval_arg": None
            }
        ]
    }
    j = job.from_cfg(cfg)
    assert j.name == cfg["name"]
    assert j.path == cfg["path"]
    assert j.params == {"whatever": 5}
    assert j.is_active == False
    assert len(j.schedule) == 2
    assert j.schedule[0].time_str() == "15:34:00"
    assert j.schedule[1].time_str() == "04:01:05"
    assert j.schedule[1].interval == Interval.daily
    assert j.schedule[1].interval_arg == None

### job
def test_job():
    j_default = job.Job(name="A", path="whatever")
    assert j_default.params==None
    assert j_default.is_active==False
    j_with_params = job.Job("B", "path", params={"a": 4}, is_active=True)
    assert j_with_params.name=="B"
    assert j_with_params.path=="path"
    assert j_with_params.params=={"a": 4}
    assert j_with_params.is_active==True

def test_job_json():
    params = "{'a': 2}"
    j = job.Job("A", "path", params, is_active=False)
    assert j.json() == {
        "name": "A",
        "path": "path",
        "params": params,
        "is_active": False,
        "schedule": []}

def test_job_with_schedule_json():
    j = job.Job("A", "path")
    s0 = Schedule(datetime.time(16,45), Interval.day, interval_arg=Day.Friday)
    s1 = Schedule(datetime.time(19,30,55), Interval.day, interval_arg=Day.Saturday)
    j.schedule.extend([s0, s1])
    ret = j.json()
    assert ret == {
        "name": "A",
        "path": "path",
        "params": None,
        "is_active": False,
        "schedule": [
            {
                "time": "16:45:00",
                "interval": Interval.day,
                "interval_arg": Day.Friday
            },
            {
                "time": "19:30:55",
                "interval": Interval.day,
                "interval_arg": Day.Saturday
            },
        ]
    }


### schedule
def test_schedule_daily():
    s = Schedule(datetime.time(4,4,4), Interval.daily)
    assert s.interval == Interval.daily
    with pytest.raises(ScheduleInitException):
        s = Schedule(datetime.time(11,1,1), Interval.daily, interval_arg="a")

def test_schedule_workday():
    s = Schedule(datetime.time(4,4,4), Interval.workday)
    assert s.interval == Interval.workday
    with pytest.raises(ScheduleInitException):
        s = Schedule(datetime.time(11,1,1), Interval.workday, interval_arg="a")

def test_schedule_day():
    s = Schedule(datetime.time(4,4,4), Interval.day, interval_arg=Day.Friday)
    assert s.interval == Interval.day
    assert s.interval_arg == Day.Friday
    with pytest.raises(ScheduleInitException):
        s = Schedule(datetime.time(11,1,1), Interval.day)

def test_schedule_json():
    s = Schedule(datetime.time(16,45), Interval.day, interval_arg=Day.Friday)
    assert s.json() == {
        "time": "16:45:00",
        "interval": Interval.day,
        "interval_arg": Day.Friday
    }