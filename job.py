
class Job:
    def __init__(self, name, path, params=None, is_active=False):
        self.name = name
        self.path = path
        self.params = params
        self.is_active = is_active
    def json(self):
        return self.__dict__
