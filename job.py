
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
