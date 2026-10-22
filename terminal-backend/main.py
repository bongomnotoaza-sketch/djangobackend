import asyncio
import os
import pty
import signal
import subprocess

from fastapi import FastAPI, WebSocket, WebSocketDisconnect


app = FastAPI()

CONTAINER_NAME = "MNOLIB641-ubuntu"


@app.websocket("/terminal")
async def terminal(websocket: WebSocket):
    await websocket.accept()

    # Make sure the container exists
    exists = subprocess.run(
        ["docker", "inspect", CONTAINER_NAME],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if exists.returncode != 0:
        await websocket.send_text(
            "\r\n\x1b[31mContainer does not exist.\x1b[0m\r\n"
        )
        await websocket.close()
        return

    # Make sure the container is running
    running = subprocess.run(
        [
            "docker",
            "inspect",
            "-f",
            "{{.State.Running}}",
            CONTAINER_NAME,
        ],
        capture_output=True,
        text=True,
    )

    if running.stdout.strip() != "true":
        subprocess.run(
            ["docker", "start", CONTAINER_NAME],
            check=True,
        )

    # --------------------------------------------------
    # CREATE A NEW PTY FOR THIS WEBSOCKET CONNECTION
    # --------------------------------------------------

    master_fd, slave_fd = pty.openpty()

    # --------------------------------------------------
    # CREATE A NEW BASH PROCESS INSIDE THE CONTAINER
    # --------------------------------------------------

    process = subprocess.Popen(
        [
            "docker",
            "exec",
            "-i",
            "-t",
            CONTAINER_NAME,
            "/bin/bash",
        ],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        close_fds=True,
        preexec_fn=os.setsid,
    )

    # Parent no longer needs the slave
    os.close(slave_fd)

    loop = asyncio.get_running_loop()

    async def read_output():
        while True:
            try:
                data = await loop.run_in_executor(
                    None,
                    os.read,
                    master_fd,
                    4096,
                )

                if not data:
                    break

                await websocket.send_bytes(data)

            except (OSError, BrokenPipeError):
                break

            except Exception:
                break

    reader_task = asyncio.create_task(read_output())

    try:
        while True:
            message = await websocket.receive()

            if message.get("type") == "websocket.disconnect":
                break

            if message.get("text") is not None:
                data = message["text"].encode()

            elif message.get("bytes") is not None:
                data = message["bytes"]

            else:
                continue

            try:
                os.write(master_fd, data)
            except (OSError, BrokenPipeError):
                break

    except WebSocketDisconnect:
        pass

    finally:

        # Stop reader
        reader_task.cancel()

        try:
            await reader_task
        except asyncio.CancelledError:
            pass

        # Close PTY
        try:
            os.close(master_fd)
        except OSError:
            pass

        # Kill THIS docker exec process only
        try:
            os.killpg(process.pid, signal.SIGHUP)
        except (ProcessLookupError, OSError):
            pass

        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            try:
                process.kill()
            except ProcessLookupError:
                pass

        try:
            await websocket.close()
        except Exception:
            pass