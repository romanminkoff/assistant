import datetime
import json
import os
import pytest

from assistant import assistant
from assistant import job
from assistant import messenger
from assistant import settings
from assistant import scheduler
from assistant.command import Cmd, Commands, _split_cmd
from assistant.scheduler import Schedule, Scheduler, Interval, Day, Event
from assistant.scheduler import ScheduleInitException, _intervals

### assistant
def test_add_job():
    a = assistant.Assistant()
    a.add_job("A", "path", params=None, is_active=False)
    assert len(a.jobs) == 1
    assert "A" in a.jobs
    a.add_job("B", "path2", params=None, is_active=False)
    assert len(a.jobs) == 2
    assert "B" in a.jobs
    with pytest.raises(assistant.AssistantAddJobException):
        a.add_job("A", "path2", params=None, is_active=False)

def test_dump_jobs():
    a = assistant.Assistant()
    a.add_job("A", "path", params=None, is_active=False)
    cfg = a.jobs_json()
    assert len(cfg["jobs"]) == 1
    assert "A" in cfg["jobs"]

_jobs_cfg = { 
    "jobs": {
        "test_job": {
            "name": "A",
            "path": "path",
            "params": [
                "whatever=5"
            ],
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
    }
}

def test_job_from_cfg():
    cfg = _jobs_cfg["jobs"]["test_job"]
    j = job.from_cfg(cfg)
    assert j.name == cfg["name"]
    assert j.path == cfg["path"]
    assert j.params == ["whatever=5"]
    assert j.is_active == False
    assert len(j.schedule) == 2
    assert j.schedule[0].time_str() == "15:34:00"
    assert j.schedule[1].time_str() == "04:01:05"
    assert j.schedule[1].interval == Interval.daily
    assert j.schedule[1].interval_arg == None

def test_make_cmd():
    j = job.Job("a", "some_path")
    assert assistant._make_cmd(j) == ["python", "some_path"]
    j = job.Job("a", "path/to/file.py", params="one=1 two=2")
    assert assistant._make_cmd(j) == [
        "python", "path/to/file.py", "one=1", "two=2"
    ]

def test_assistant_add_scheduled_jobs():
    a = assistant.Assistant()
    assistant._load_jobs(a, _jobs_cfg)
    sched_len = len(_jobs_cfg["jobs"]["test_job"]["schedule"])
    assert len(a.scheduler._s.jobs) == sched_len
    sched_job = a.scheduler._s.jobs[0]
    assert sched_job.unit == "weeks"
    assert sched_job != a.scheduler._s.jobs[1]

def test_assistant_schedule_workdays_job():
    a = assistant.Assistant()
    a.add_job("A", "path", params=None, is_active=False)
    s = Schedule(datetime.time(16,45), Interval.workdays)
    a.reschedule_job("A", s)
    assert len(a.scheduler._s.jobs) == 5
    a.scheduler.cancel_events("A")
    assert len(a.scheduler._s.jobs) == 0


###
### job
###
def test_job():
    j_default = job.Job(name="A", path="whatever")
    assert j_default.params==None
    assert j_default.is_active==False
    j_with_params = job.Job("B", "path", params="a=4", is_active=True)
    assert j_with_params.name=="B"
    assert j_with_params.path=="path"
    assert j_with_params.params=="a=4"
    assert j_with_params.is_active==True

def test_job_json():
    params = "a=2"
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
    j = job.Job("a", "", params="a=1 b=bb")
    assert j.params_list() == ["a=1", "b=bb"]

### scheduler
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

def test_scheduler_next_job_run():
    a = assistant.Assistant()
    a.add_job("A", "path", params=None, is_active=True)
    in_15_minutes = datetime.datetime.now() + datetime.timedelta(minutes=15)
    in_15_minutes = in_15_minutes.replace(microsecond=0)
    s = Schedule(in_15_minutes.time(), Interval.workdays)
    a.reschedule_job("A", s)
    in_5_minutes = datetime.datetime.now() + datetime.timedelta(minutes=5)
    in_5_minutes = in_5_minutes.replace(microsecond=0)
    s = Schedule(in_5_minutes.time(), Interval.daily)
    a.reschedule_job("A", s)
    assert a.next_run() == in_5_minutes
    a.scheduler.cancel_events("A")
    assert a.next_run() == None

def test_interval():
    intervals = [
        scheduler.Interval.daily,
        scheduler.Interval.weekday,
        scheduler.Interval.workdays
    ]
    assert set(scheduler.Interval.list()) == set(intervals)

###
### messenger
###
def test_send_text_msg_exception():
    with pytest.raises(messenger.UnsupportedMessengerException):
        messenger.send_message(msgr_cfg={"name": "bla"}, payload=None)

def test_to_slack_channel_name():
    test_vals = {
        'Some': 'some',
        'Some nAmE': 'some_name'
    }
    for test, ref in test_vals.items():
        assert messenger._to_slack_channel_name(test) == ref

def test_is_slack_connection_ok():
    # this should work if internet connection is OK
    assert messenger._is_slack_connection_ok()

def test_slack_channels():
    class Result:
        data = {'ok': True, 'channels': [{'name': 'a'}, {'name': 'b'}]}
    class Client:
        def conversations_list(self):
            return Result()
    assert messenger._slack_channels(Client()) == ['a', 'b']

def test_slack_send_message_main_raises_on_bad_token():
    cfg = {'token': None}
    with pytest.raises(messenger.MessengerClientAuthSetupException):
        messenger._slack_send_message_main(cfg=cfg, payload=None)

###
### settings
###
def test_messenger_cfg():
    s = {"messenger": {"name": "slack"}}
    cfg = settings.messenger_cfg(s)
    assert cfg["name"] == "slack"
    cfg = settings.messenger_cfg({'bla': 1})
    assert cfg == None

def test_create_settings_file():
    p = settings.create_settings_file(fname="_test_settings.json")
    assert os.path.exists(p)
    with open(p) as f:
        content = json.load(f)
    os.remove(p)
    assert content.get('messenger')

###
### command
###
class CmdExecutedException(Exception):
    pass

def _cmd(arg):
    raise CmdExecutedException()

def test_commands_default_command():
    c = Commands()
    c1 = Cmd(['def','c'], _cmd, 'Default command')
    c.add(c1, default=True)
    assert c.cmd('d').help_str == 'Default command'

def test_commands_get_cmd():
    c = Commands()
    c1 = Cmd(['cmd','c'], _cmd, 'CMD command')
    c.add(c1)
    c2 = Cmd(['do'], _cmd, 'Do command')
    c.add(c2)
    assert c.cmd('cmd').help_str == 'CMD command'
    assert c.cmd('c').help_str == 'CMD command'
    assert c.cmd('do').help_str == 'Do command'
    assert c.cmd('cmd').callback == _cmd
    assert c.cmd('do').callback == _cmd

def test_help_str():
    c = Commands()
    c1 = Cmd(['cmd','c'], _cmd, 'C cmd')
    c.add(c1)
    c2 = Cmd(['do'], _cmd, 'D cmd')
    c.add(c2)
    help_str = '  Commands:\n    cmd, c: C cmd\n    do: D cmd'
    print(c.help())
    assert c.help() == help_str

def test_commands_call_cmd():
    c = Commands()
    c1 = Cmd(['cmd','c'], _cmd, 'A command')
    c.add(c1)
    with pytest.raises(CmdExecutedException):
        c.call('cmd', 'a')

def test_commands_call_cmd_shortcut():
    c = Commands()
    c1 = Cmd(['cmd','c'], _cmd, 'A command')
    c.add(c1)
    with pytest.raises(CmdExecutedException):
        c.call('c', 'a')

def test_cmd_help_str():
    c1 = Cmd(['cmd'], _cmd, 'CMD command')
    assert c1.help() == 'cmd: CMD command'
    c1 = Cmd(['cmd','c'], _cmd, 'CMD command')
    assert c1.help() == 'cmd, c: CMD command'

class CmdExecutedException(Exception):
    pass

class CmdSubExecutedException(Exception):
    pass

def _cmd(arg):
    raise CmdExecutedException()

def _cmd_sub(arg):
    raise CmdSubExecutedException()

def test_add_subcommand():
    c = Commands()
    c1 = Cmd(['c1'], _cmd, 'Cmd 1')
    c1_1 = Cmd(['c11'], _cmd_sub, 'Sub cmd 1')
    c1.add_subcmd(c1_1)
    c.add(c1)
    assert len(c1.cmds) == 1
    assert c1.cmds[0].help() == 'c11: Sub cmd 1'

def test_call_subcommand():
    c = Commands()
    c1_main = Cmd(['c1'], help='Cmd main')
    c1_sub1 = Cmd(['c1_1'], help='Cmd 1->1')
    c1_s1_s1 = Cmd(['c1_1_1'], _cmd_sub, help='Cmd 1->1->1')

    c1_sub1.add_subcmd(c1_s1_s1)
    c1_main.add_subcmd(c1_sub1)
    c.add(c1_main)
    
    with pytest.raises(CmdSubExecutedException):
        c.call('c1.c1_1.c1_1_1', None)

def test_subcommand_help():
    c1_main = Cmd(['c1'], help='Cmd main')
    c1_s1 = Cmd(['c1_1'], help='Cmd 1->1')
    c1_s1_s1 = Cmd(['c1_1_1', 'u'], _cmd_sub, help='Cmd 1->1->1')

    c1_s1.add_subcmd(c1_s1_s1)
    c1_main.add_subcmd(c1_s1)

    assert c1_s1_s1.help() == 'c1_1_1, u: Cmd 1->1->1'
    assert c1_s1.help() == 'c1_1: Cmd 1->1. Sub-commands: c1_1_1, u.'

def test_callback_call_when_subcommands_present():
    c = Commands()
    c1_main = Cmd(['c1'], help='Cmd main')
    c1_s1 = Cmd(['c1_1'], _cmd_sub, help='Cmd 1->1')
    c1_s1_s1 = Cmd(['c1_1_1'], None, help='Cmd 1->1->1')

    c1_s1.add_subcmd(c1_s1_s1)
    c1_main.add_subcmd(c1_s1)
    c.add(c1_main)

    with pytest.raises(CmdSubExecutedException):
        c.call('c1.c1_1', None)

def test_split_cmd():
    cases = {
        '': ['', ''],
        'aaa': ['aaa', ''],
        'aa.bb': ['aa', 'bb'],
        'aa.bb.cc': ['aa', 'bb.cc']
    }
    for k, res in cases.items():
        a, b = _split_cmd(k)
        assert res == [a,b]