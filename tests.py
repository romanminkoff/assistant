import datetime
import pytest

import assistant
import job
from scheduler import Schedule, Scheduler, Interval, Day, Event
from scheduler import ScheduleInitException, _intervals


### assistant
def test_add_job():
    jm = assistant.JobManager()
    jm.add_job("A", "path", params=None, is_active=False)
    assert len(jm.jobs) == 1
    assert "A" in jm.jobs
    with pytest.raises(assistant.AssistantAddJobException):
        jm.add_job("A", "path2", params=None, is_active=False)

def test_dump_jobs():
    jm = assistant.JobManager()
    jm.add_job("A", "path", params=None, is_active=False)
    cfg = jm.jobs_json()
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
                "interval": "weekday",
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
    s0 = Schedule(datetime.time(16,45), Interval.weekday, interval_arg=Day.Friday)
    s1 = Schedule(datetime.time(19,30,55), Interval.weekday, interval_arg=Day.Saturday)
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
                "interval": Interval.weekday,
                "interval_arg": Day.Friday
            },
            {
                "time": "19:30:55",
                "interval": Interval.weekday,
                "interval_arg": Day.Saturday
            },
        ]
    }

def test_job_params_list():
    j = job.Job("a", "", params={"a": 1, "b": "bb"})
    assert j.params_list() == ["a", "1", "b", "bb"]

### schedule
def test_schedule_daily():
    s = Schedule(datetime.time(4,4,4), Interval.daily)
    assert s.interval == Interval.daily
    with pytest.raises(ScheduleInitException):
        s = Schedule(datetime.time(11,1,1), Interval.daily, interval_arg="a")

def test_schedule_workday():
    s = Schedule(datetime.time(4,4,4), Interval.workdays)
    assert s.interval == Interval.workdays
    with pytest.raises(ScheduleInitException):
        s = Schedule(datetime.time(11,1,1), Interval.workdays, interval_arg="a")

def test_schedule_day():
    s = Schedule(datetime.time(4,4,4), Interval.weekday, Day.Friday)
    assert s.interval == Interval.weekday
    assert s.interval_arg == Day.Friday
    with pytest.raises(ScheduleInitException):
        s = Schedule(datetime.time(11,1,1), Interval.weekday)

def test_schedule_json():
    s = Schedule(datetime.time(16,45), Interval.weekday, Day.Friday)
    assert s.json() == {
        "time": "16:45:00",
        "interval": Interval.weekday,
        "interval_arg": Day.Friday
    }

def test_schedule_intervals():
    assert len(_intervals[Interval.weekday]) == 7
    assert Day.Sunday in _intervals[Interval.weekday]

def test_schedule_raise_on_incorrect_time():
    with pytest.raises(ScheduleInitException):
        Schedule("11:20:00", Interval.daily)

def _test_runner(a, b):
    pass

def test_scheduler_flow():
    s = Scheduler(_test_runner, None)
    t = datetime.datetime.now() + datetime.timedelta(seconds=10)
    t1 = t.time()
    s.schedule_event(Event(name="TestEvent", schedule=Schedule(t1, "daily")))
    assert len(s._s.jobs) == 1
    assert s._s.jobs[0].next_run.second == t.second
    assert s._s.jobs[0].next_run.minute == t.minute
    assert len(s.jobs) == 1
    assert "TestEvent" in s.jobs
    t2 = (t + datetime.timedelta(seconds=20)).time()
    s.schedule_event(Event(name="TestEvent", schedule=Schedule(t2, "daily")))
    assert len(s.jobs) == 1
    assert len(s.jobs["TestEvent"]) == 2
    assert len(s._s.jobs) == 2
    s.cancel_events("TestEvent")
    assert len(s._s.jobs) == 0
    assert len(s.jobs) == 0