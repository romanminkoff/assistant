from datetime import datetime

from scheduler import Schedule, TIME_FMT


class Job:
    def __init__(self, name, path, params=None, is_active=False):
        self.name = name
        self.path = path
        self.params: dict = params
        self.is_active = is_active
        self.schedule = []
    def schedule_json(self):
        return [s.json() for s in self.schedule]
    def json(self):
        r = self.__dict__.copy()
        r["schedule"] = self.schedule_json()
        return r
    def params_list(self):
        if self.params:
            lst = []
            for k, v in self.params.items():
                lst.extend([str(k), str(v)])
            return lst

def from_cfg(cfg_dict):
    c = cfg_dict
    j = Job(c["name"], c["path"], c["params"], c["is_active"])
    for s in c["schedule"]:
        t = datetime.strptime(s["time"], TIME_FMT).time()
        j.schedule.append(Schedule(t, s["interval"], s["interval_arg"]))
    return j
