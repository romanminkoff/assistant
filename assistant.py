import os
import sys

import job

EXCEPTIONS_LIMIT = 5
INPUT_CHAR = "> "

jobs = []

def print_available_commands():
    print(f"Available commands: {list(commands.keys())}")

def cmd_help():
    print("Usage: enter command.")
    print_available_commands()

def cmd_exit():
    print("Have a nice day!")
    sys.exit(0)

def cmd_list_jobs():
    for i, job in enumerate(jobs):
        print(f"  {i}:  {job.__dict__}")

def _add_job(name, path, params, is_active):
    j = job.Job(name, path, params, is_active)
    jobs.append(j)

def cmd_add_job():
    name = input("  Name: ")
    path = input("  Path: ")
    params = input("  Params (opt): ") or None
    is_active = input("  Is active? y/n: ")
    is_active = True if is_active.lower() == "y" else False

    is_input_correct = input("  Is input correct? Create this job? y/n: ")

    if is_input_correct.lower() == "y":
        _add_job(name, path, params, is_active)
        print(f"  Job {name} was added.")

commands = {
    "help": cmd_help,
    "q": cmd_exit,
    "jobs": cmd_list_jobs,
    "add job": cmd_add_job,
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


if __name__ == "__main__":
    main()