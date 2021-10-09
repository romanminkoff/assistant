import os
import sys

EXCEPTIONS_LIMIT = 5
INPUT_CHAR = "> "

def cmd_help():
    print("TODO: cmd_help")

def cmd_exit():
    print("Have a nice day!")
    sys.exit(0)

commands = {
    "help": cmd_help,
    "q": cmd_exit
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


##### Tests

__mock_input_string = ""
def _mock_input():
    return __mock_input_string


#  - keep jobs
#  - add jobs
#  - show jobs
#  - enable/disable jobs
#  - show jobs status (upgrade prev.)