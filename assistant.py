import json
import os
import sys

import job

EXCEPTIONS_LIMIT = 5
INPUT_CHAR = "> "

jobs = {}

def print_available_commands():
    print(f"Available commands: {list(commands.keys())}")

def cmd_help():
    print("Usage: enter command.")
    print_available_commands()

def cmd_exit():
    print("Have a nice day!")
    sys.exit(0)

def cmd_list_jobs():
    for name, job in jobs.items():
        print(f"  {name}:  {job.json()}")

class AssistantAddJobException(Exception):
    pass

def _add_job(name, path, params, is_active):
    if name in jobs:
        raise AssistantAddJobException(f"Job {name} is already in the list.")
    j = job.Job(name, path, params, is_active)
    jobs.update({name: j})

def cmd_add_job():
    name = input("  Name: ")
    path = input("  Path: ")
    params = input("  Params (opt): ") or None
    is_active = input("  Is active? y/(n): ")
    is_active = True if is_active.lower() == "y" else False

    is_input_correct = input("  Is input correct? Create this job? (y)/n: ")

    if is_input_correct.lower() != "n":
        _add_job(name, path, params, is_active)
        print(f"  Job <{name}> was added.")

def _jobs_config_json():
    cfg = {"jobs": {}}
    for name, j in jobs.items():
        j_str = j.json()
        cfg["jobs"].update({name: j_str})
    return cfg

def cmd_save_jobs():
    print("  Save jobs configuration to file (json format).")
    name = input("  Enter file name: ")
    if os.path.exists(name):
        print("  (!) File with this name already exists. Please pick another name.")
        return
    jobs_json = _jobs_config_json()
    with open(name, "wt") as f:
        json.dump(jobs_json, f, indent=4)

def _load_jobs(cfg):
    for _, job_cfg in cfg["jobs"].items():
        j = job.from_cfg(job_cfg)
        jobs.update({j.name: j})

def _load_job_from_file(name):
    with open(name) as f:
        cfg = json.load(f)
    _load_jobs(cfg)

def cmd_load_jobs_from_config():
    name = input("  Config file path: ")
    if not os.path.exists(name):
        print(f"  File {name} doesn't exists.")
        return
    _load_job_from_file(name)

commands = {
    "help": cmd_help,
    "q": cmd_exit,
    "jobs": cmd_list_jobs,
    "j": cmd_list_jobs,
    "add job": cmd_add_job,
    "save jobs": cmd_save_jobs,
    "load jobs": cmd_load_jobs_from_config,
}

def input_cmd():
    s = input(INPUT_CHAR)
    if cmd := commands.get(s):
        return cmd
    else:
        print(f"Unrecognized command <{s}>.")
        return cmd_help

def main():
    attempts_to_continue = 0
    while(attempts_to_continue < EXCEPTIONS_LIMIT):
        try:
            cmd = input_cmd()
            cmd()
        except KeyboardInterrupt:
            cmd_exit()
        except SystemExit:
            os._exit(0)
        except:
            print(f"Error: {sys.exc_info()[0]}. Trying to continue...")
            attempts_to_continue += 1
    print("Exit due to many occurred exceptions.")

def reset():
    """Clean up everything.
       Currently assistant is implemented as a 'singleton'."""
    jobs.clear()

if __name__ == "__main__":
    main()