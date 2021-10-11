from datetime import datetime

from schedule import Schedule, TIME_FMT


class Job:
    def __init__(self, name, path, params=None, is_active=False):
        self.name = name
        self.path = path
        self.params = params
        self.is_active = is_active
        self.schedule = []
    def json(self):
        r = self.__dict__.copy()
        r["schedule"] = [s.json() for s in self.schedule]
        return r

def from_cfg(cfg_dict):
    c = cfg_dict
    j = Job(c["name"], c["path"], c["params"], c["is_active"])
    for s in c["schedule"]:
        t = datetime.strptime(s["time"], TIME_FMT).time()
        j.schedule.append(Schedule(t, s["interval"], s["interval_arg"]))
    return j
