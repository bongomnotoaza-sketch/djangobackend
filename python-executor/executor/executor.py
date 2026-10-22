import subprocess
import tempfile
import os
import threading
import sys

IMAGE = "logictree-python"


def execute(code):
    with tempfile.TemporaryDirectory() as temp_dir:
        code_file = os.path.join(temp_dir, "main.py")
        with open(code_file, "w") as f:
            f.write(code)

        process = subprocess.Popen(
            [
                "docker", "run", "--rm", "-i",
                "-v", f"{temp_dir}:/workspace",
                IMAGE, "python", "-u", "/workspace/main.py",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,
        )

        stop_event = threading.Event()

        def read_stdout():
            while not stop_event.is_set():
                char = process.stdout.read(1)
                if not char:
                    break
                print(char, end="", flush=True)

        def read_stdin():
            while not stop_event.is_set() and process.poll() is None:
                try:
                    line = sys.stdin.readline()  # blocking, can't be cancelled
                    if line == "" or process.poll() is not None:
                        break
                    process.stdin.write(line)
                    process.stdin.flush()
                except (EOFError, BrokenPipeError, ValueError):
                    break

        stdout_thread = threading.Thread(target=read_stdout, daemon=True)
        stdin_thread = threading.Thread(target=read_stdin, daemon=True)
        stdout_thread.start()
        stdin_thread.start()

        try:
            process.wait()
        finally:
            stop_event.set()
            stdout_thread.join(timeout=2)
            stdin_thread.join(timeout=0.1)  # best-effort; can't force-kill a blocked readline

        stderr = process.stderr.read()
        return {"returncode": process.returncode, "stderr": stderr}


if __name__ == "__main__":
    code = '''
print("Starting infinite loop")

while True:
    pass
'''
    result = execute(code)
    print("\nSTDERR:")
    print(result["stderr"])
    print("RETURN CODE:")
    print(result["returncode"])