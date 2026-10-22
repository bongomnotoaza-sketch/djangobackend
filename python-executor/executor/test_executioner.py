import threading
import sys

from executioner import Executioner


executioner = Executioner()


code = '''
print("Python program started")

name = input("What is your name? ")

print(f"Hello {name}")

age = input("How old are you? ")

print(f"You are {age} years old")
'''


execution = executioner.start(code)


def terminal_input():

    while execution.process.poll() is None:

        try:
            line = sys.stdin.readline()

            if not line:
                break

            execution.send_input(line.rstrip("\n"))

        except (EOFError, BrokenPipeError, ValueError):
            break


input_thread = threading.Thread(
    target=terminal_input,
    daemon=True,
)

input_thread.start()


while execution.process.poll() is None:

    output = execution.read_output(timeout=0.1)

    if output is not None:
        print(output, end="", flush=True)


execution.wait()


# Read anything remaining in the queue
while True:

    output = execution.read_output(timeout=0.1)

    if output is None:
        break

    print(output, end="", flush=True)


print("\nRETURN CODE:")
print(execution.process.returncode)