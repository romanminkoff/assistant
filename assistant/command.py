
class Cmd:
    def __init__(self, cmd_list, call, help):
        self.cmd_list = cmd_list
        self.call = call
        self.help = help

    def help_str(self):
        return f'{", ".join(self.cmd_list)}: {self.help}'

class Commands:
    def __init__(self):
        self.cmds = []
        self._default = None

    def add(self, cmd, default=False):
        self.cmds.append(cmd)
        if default:
            self._default = cmd

    def cmd(self, cmd_name):
        for c in self.cmds:
            if cmd_name in c.cmd_list:
                return c
        return self._default

    def call(self, cmd_name, arg):
        self.cmd(cmd_name).call(arg)

    def help(self):
        txt = '  Commands:'
        for c in self.cmds:
            txt = f'{txt}\n    {c.help_str()}'
        return txt
