from datetime import datetime
import json
import os
import pprint
import subprocess
import sys
import threading

from . import api
from . import command
from . import job
from . import messenger
from . import settings
from . import scheduler


EXCEPTIONS_LIMIT = 5
INPUT_CHAR = "> "


class AssistantAddJobException(Exception):
    pass

def _msg_from_broker(json_obj):
    msg = json.loads(json_obj)
    msgr_cfg = settings.messenger_cfg(settings.from_file())
    txt = msg.get("text")
    messenger.send_text_msg(msgr_cfg, txt)

def _make_cmd(job: job.Job):
    cmd = ["python", job.path]
    if job.params:
        cmd.extend(job.params_list())
    return cmd

def _job_runner(a, name):
    cmd = _make_cmd(a.jobs.get(name))
    print(f"  Launching scheduled job: {' '.join(cmd)}")
    subprocess.run(cmd)

class Assistant:
    def __init__(self, msg_from_broker=_msg_from_broker):
        self.jobs = {}
        self.scheduler = scheduler.Scheduler(_job_runner, runner_arg=self)
        self._listen_msg_broker(msg_from_broker)
        self._check_settings_file()
    
    def _check_settings_file(self):
        s = settings.from_file()
        if not s:
            fname = settings.create_settings_file()
            print(f'NOTE: creating default settings file {fname}')

    def _listen_msg_broker(self, msg_from_broker):
        t = threading.Thread(group=None, target=api.receiver,
            args=(msg_from_broker,), daemon=True)
        t.start()

    def _add_schedule_job(self, j):
        self.jobs.update({j.name: j})
        self._reschedule_job(j.name)

    def add_job(self, name, path, params, is_active):
        if name in self.jobs:
            raise AssistantAddJobException(f"Job {name} is already in the list.")
        j = job.Job(name, path, params, is_active)
        self._add_schedule_job(j)

    def add_job_from_json(self, job_dict):
        j = job.from_cfg(job_dict)
        self._add_schedule_job(j)

    def jobs_json(self):
        cfg = {"jobs": {}}
        for name, j in self.jobs.items():
            j_str = j.json()
            cfg["jobs"].update({name: j_str})
        return cfg

    def pprint_jobs(self):
        for _, job in self.jobs.items():
            pprint.pprint(job.json())

    def reschedule_job(self, name, sched):
        self.jobs[name].schedule.append(sched)
        self._reschedule_job(name)

    def _reschedule_job(self, name):
        self.scheduler.cancel_events(name)
        for s in self.jobs[name].schedule:
            e = scheduler.Event(name, s)
            self.scheduler.schedule_event(e)

    def next_run(self):
        return self.scheduler.next_run()


def cmd_next_job_run(a):
    print(a.next_run())

def cmd_exit(a):
    print("Have a nice day!")
    sys.exit(0)

def cmd_list_jobs(a):
    a.pprint_jobs()

def cmd_add_job(a):
    name = input("  Name: ")
    path = input("  Path: ")
    params = input("  Params (opt): ") or None
    is_active = input("  Is active? y/[n]: ")
    is_active = True if is_active.lower() == "y" else False
    is_input_correct = input("  Is input correct? Create this job? [y]/n: ")
    if is_input_correct.lower() != "n":
        a.add_job(name, path, params, is_active)
        print(f"  Job <{name}> was added.")

def cmd_save_jobs(a):
    print("  Save jobs configuration to file in json format.")
    name = input("  Enter file name: ")
    if os.path.exists(name):
        print("  (!) File with this name already exists. Please pick another name.")
        return
    jobs_json = a.jobs_json()
    with open(name, "wt") as f:
        json.dump(jobs_json, f, indent=4)
    print(f"  File <name> was created.")

def _load_jobs(a, cfg):
    for _, job_cfg in cfg["jobs"].items():
        a.add_job_from_json(job_cfg)

def _load_jobs_from_file(a, name):
    with open(name) as f:
        cfg = json.load(f)
    _load_jobs(a, cfg)

def cmd_load_jobs_from_config(a):
    fname = input("  Config file path: ")
    if not os.path.exists(fname):
        print(f"  File {fname} doesn't exists.")
        return
    _load_jobs_from_file(a, fname)

def cmd_schedule_job(a: Assistant):
    name = input("  Job name: ")
    if not name in a.jobs:
        print(f"  Job <{name}> doesn't exists.")
        return
    t = input(f"  Time ({scheduler.TIME_FMT}): ")
    t = datetime.strptime(t, scheduler.TIME_FMT).time()
    _i_options = scheduler.Interval.list()
    interval = input(f"  Interval ({_i_options}): ")
    if not interval in _i_options:
        print(f"  Incorrect interval ({interval})")
        return
    interval_arg = None
    if _a_options := scheduler._intervals[interval]:
        interval_arg = input(f"  Interval argument ({_a_options}): ")
        if not interval_arg in _a_options:
            print(f"  Incorrect argument ({interval_arg})")
            return
    s = scheduler.Schedule(t, interval, interval_arg)
    a.reschedule_job(name, s)
    print(f"  Job was rescheduled ({a.jobs[name].schedule_json()})")

def commands():
    c = command.Commands()
    c.add(command.Cmd(['q'], cmd_exit, 'Quit'))

    jobs = command.Cmd(['jobs','j'], cmd_list_jobs, 'List jobs')
    j_add = command.Cmd(['add'], cmd_add_job, 'Add a new job')
    jobs.add_subcmd(j_add)
    j_save = command.Cmd(['save'], cmd_save_jobs, 'Save jobs to a file')
    jobs.add_subcmd(j_save)
    j_load = command.Cmd(['load'], cmd_load_jobs_from_config,
                         'Load jobs from a file')
    jobs.add_subcmd(j_load)
    j_sched = command.Cmd(['schedule','sched'], cmd_schedule_job,
                          'Schedule specific job')
    jobs.add_subcmd(j_sched)
    j_next = command.Cmd(['next_run','next'], cmd_next_job_run,
                       'Print time when the next job should run')
    jobs.add_subcmd(j_next)
    c.add(jobs)
    return c

def main():
    a = Assistant()
    cmds = commands()
    attempts_to_continue = 0
    while(attempts_to_continue < EXCEPTIONS_LIMIT):
        try:
            cmd_name = input(INPUT_CHAR)
            cmds.call(cmd_name, a)
        except KeyboardInterrupt:
            cmd_exit()
        except SystemExit:
            os._exit(0)
        except:
            print(f"Error: {sys.exc_info()[0]}. Trying to continue...")
            attempts_to_continue += 1
    print("Exit due to many occurred exceptions.")

if __name__ == "__main__":
    main()