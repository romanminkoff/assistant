import datetime
import schedule
import time
import threading


class Interval:
    daily = "daily"
    workdays = "workdays"
    weekday = "weekday"
    @staticmethod
    def list():
        return ["daily", "workdays", "weekday"]

class Day:
    Sunday = "Sunday"
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
    Saturday = "Saturday"
    @staticmethod
    def list():
        return ["Sunday", "Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday", "Saturday"]
    @staticmethod
    def workDays():
        return ["Monday", "Tuesday", "Wednesday",
                "Thursday", "Friday"]

_intervals = {
    Interval.daily: [],
    Interval.workdays: [],
    Interval.weekday: Day.list()
}

class ScheduleInitException(Exception):
    pass

TIME_FMT = "%H:%M:%S"

class Schedule:
    """Schedule time, interval and interval argument if needed."""
    def __init__(self, time: datetime.time, interval: str, interval_arg=None):
        if _intervals[interval]:
            if not interval_arg in _intervals[interval]:
                raise ScheduleInitException("Incorrect interval argument.")
        else:
            if interval_arg:
                raise ScheduleInitException("Incorrect interval argument.")
        if not isinstance(time, datetime.time):
            raise ScheduleInitException("Time must be datetime.time")
        self.time = time
        self.interval = interval
        self.interval_arg = interval_arg
    def time_str(self, fmt=TIME_FMT):
        return self.time.strftime(fmt)
    def json(self):
        r = self.__dict__.copy()
        r["time"] = self.time_str()
        return r


class Event:
    def __init__(self, name, schedule):
        self.name = name
        self.schedule = schedule


def _schedule_run_pending(_schedule):
    while True:
        _schedule.run_pending()
        time.sleep(1)

def _run_event_non_blocking(runner, arg, name):
    t = threading.Thread(group=None, target=runner, args=(arg, name),
        daemon=True)
    t.start()

def _scheduler_runner(*args):
    sched, event = args[0]
    _run_event_non_blocking(sched.job_runner, sched.job_runner_arg, event.name)

class Scheduler:
    def __init__(self, runner, runner_arg):
        self.jobs = {}  # {name: [job,]}
        self.job_runner = runner
        self.job_runner_arg = runner_arg
        self._s = schedule.Scheduler()
        self._run_scheduler_non_blocking()
    
    def __del__(self):
        self._s.clear()

    def _run_scheduler_non_blocking(self):
        self._t = threading.Thread(group=None, target=_schedule_run_pending,
            args=(self._s,), daemon=True)
        self._t.start()

    def _add_job(self, name, job):
        if name in self.jobs:
            self.jobs[name].append(job)
        else:
            self.jobs.update({name: [job]})

    def schedule_event(self, event: Event):
        t = event.schedule.time_str()
        if event.schedule.interval == Interval.daily:
            j = self._s.every().day.at(t).do(_scheduler_runner, (self, event))
            self._add_job(event.name, j)
        elif event.schedule.interval == Interval.weekday:
            weekday = event.schedule.interval_arg.lower()
            sched_day = getattr(self._s.every(), weekday)
            j = sched_day.at(t).do(_scheduler_runner, (self, event))
            self._add_job(event.name, j)
        elif event.schedule.interval == Interval.workdays:
            for day in Day.workDays():
                sched_day = getattr(self._s.every(), day.lower())
                j = sched_day.at(t).do(_scheduler_runner, (self, event))
                self._add_job(event.name, j)
        

    def cancel_events(self, name):
        if jobs := self.jobs.get(name):
            for j in jobs:
                self._s.cancel_job(j)
            del self.jobs[name]
    
    def next_run(self):
        return self._s.next_run