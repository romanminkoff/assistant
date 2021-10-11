import datetime

class Interval:
    daily = "daily"
    workday = "workday"
    day = "day"
    @staticmethod
    def list():
        return ["daily", "workday", "day"]

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

_intervals = {
    Interval.daily: [],
    Interval.workday: [],
    Interval.day: Day.list()
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
    def time_str(self):
        return self.time.strftime(TIME_FMT)
    def json(self):
        r = self.__dict__.copy()
        r["time"] = self.time_str()
        return r


# schedule.every().day.at("00:00").do(job)  # returns job
# schedule.every().tuesday.at("18:00").do()  # returns job
# schedule.cancel_job(job)
# while True:
#     schedule.run_pending()
#     time.sleep(1)

# s = sched.scheduler(time.time, time.sleep)
# s.enter(10, 1, print_time)
# s.run()
# s.cancel(event)