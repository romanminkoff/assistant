import datetime

class Interval:
    daily = "daily"
    workday = "workday"
    day = "day"

class Day:
    Sunday = "Sunday"
    Monday = "Monday"
    Tuesday = "Tuesday"
    Wednesday = "Wednesday"
    Thursday = "Thursday"
    Friday = "Friday"
    Saturday = "Saturday"
    @staticmethod
    def days():
        return Day.__dict__

_intervals = {
    Interval.daily: [None],
    Interval.workday: [None],
    Interval.day: Day.days(),
}

class ScheduleInitException(Exception):
    pass

TIME_FMT = "%H:%M:%S"

class Schedule:
    """Schedule time, interval and interval argument if needed."""
    def __init__(self, time: datetime.time, interval: str, interval_arg=None):
        if not interval_arg in _intervals[interval]:
            raise ScheduleInitException("Incorrect interval settings.")
        self.time = time
        self.interval = interval
        self.interval_arg = interval_arg
    def time_str(self):
        return self.time.strftime(TIME_FMT)
    def json(self):
        r = self.__dict__
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