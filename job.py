from datetime import time

from schedule import Schedule


class Job:
    def __init__(self, name, path, params=None, is_active=False):
        self.name = name
        self.path = path
        self.params = params
        self.is_active = is_active
        self.schedule = []
    def json(self):
        r = self.__dict__
        r["schedule"] = [s.json() for s in self.schedule]
        return r

def from_cfg(cfg_dict):
    c = cfg_dict
    j = Job(c["name"], c["path"], c["params"], c["is_active"])
    for s in c["schedule"]:
        t = time.fromisoformat(s["time"])
        j.schedule.append(Schedule(t, s["interval"], s["interval_arg"]))
    return j
