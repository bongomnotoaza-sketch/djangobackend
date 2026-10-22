import subprocess
import tempfile
import os
import threading
import queue


class Execution:

    def __init__(self, process, temp_dir):

        self.process = process
        self.temp_dir = temp_dir

        self.stop_event = threading.Event()

        self.stdout = []
        self.stderr = ""

        self.output_queue = queue.Queue()

        self.stdout_thread = threading.Thread(
            target=self._read_stdout,
            daemon=True,
        )

        self.stdout_thread.start()

    def _read_stdout(self):

        while not self.stop_event.is_set():

            char = self.process.stdout.read(1)

            if not char:
                break

            self.stdout.append(char)
            self.output_queue.put(char)

    def read_output(self, timeout=None):

        try:
            return self.output_queue.get(
                timeout=timeout
            )

        except queue.Empty:
            return None

    def send_input(self, value):

        self.process.stdin.write(value + "\n")
        self.process.stdin.flush()

    def wait(self):

        self.process.wait()

        self.stop_event.set()

        self.stdout_thread.join(timeout=2)

        self.stderr = self.process.stderr.read()

    def result(self):

        return {
            "stdout": "".join(self.stdout),
            "stderr": self.stderr,
            "returncode": self.process.returncode,
        }


class Executioner:

    IMAGE = "logictree-python"

    def start(self, code):

        temp_dir = tempfile.TemporaryDirectory()

        code_file = os.path.join(
            temp_dir.name,
            "main.py"
        )

        with open(code_file, "w") as f:
            f.write(code)

        process = subprocess.Popen(
            [
                "docker",
                "run",
                "--rm",
                "-i",
                "-v",
                f"{temp_dir.name}:/workspace",
                self.IMAGE,
                "python",
                "-u",
                "/workspace/main.py",
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=0,
        )

        return Execution(
            process,
            temp_dir,
        )