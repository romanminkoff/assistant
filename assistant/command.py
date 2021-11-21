import re


def _split_cmd(txt):
    if m := re.findall(r'(^\w+)[.]*(\S*)', txt):
        return m[0][0], m[0][1]
    else:
        return '', ''


class Cmd:
    def __init__(self, cmd_list, call=None, help=""):
        self.cmd_list = cmd_list
        self.callback = call or self.print_help
        self.help_str = help
        self.cmds = []
    
    def add_subcmd(self, cmd):
        self.cmds.append(cmd)

    def cmd(self, cmd_name):
        for c in self.cmds:
            if cmd_name in c.cmd_list:
                return c

    def call(self, sub_cmds, *args):
        cmd_name, sub_cmds = _split_cmd(sub_cmds)
        if cmd_name:
            if cmd := self.cmd(cmd_name):
                cmd.call(sub_cmds, *args)
            else:
                self.print_help()
        else:
            self.callback(*args)

    def help(self):
        h = f'{", ".join(self.cmd_list)}: {self.help_str}'
        if self.cmds:
            sub_names = []
            for c in self.cmds:
                sub_names.extend(c.cmd_list)
            h = f'{h}. Sub-commands: {", ".join(sub_names)}.'
        return h

    def print_help(self):
        print(f'  {self.help()}')

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
        if self._default:
            return self._default

    def call(self, cmd_name, arg):
        cmd_name, sub_cmds = _split_cmd(cmd_name)
        if cmd := self.cmd(cmd_name):
            cmd.call(sub_cmds, arg)
        else:
            self.print_help()

    def help(self):
        txt = '  Commands:'
        for c in self.cmds:
            txt = f'{txt}\n    {c.help()}'
        return txt
    
    def print_help(self):
        print(self.help())
