import websocket
import threading
import sys


ws = websocket.create_connection(
    "ws://localhost:4000/terminal"
)


def receive_output():
    while True:
        try:
            data = ws.recv()

            if data is None:
                break

            if isinstance(data, bytes):
                sys.stdout.buffer.write(data)
                sys.stdout.buffer.flush()
            else:
                print(data, end="", flush=True)

        except Exception:
            break


threading.Thread(
    target=receive_output,
    daemon=True,
).start()


try:
    while True:
        data = input()

        ws.send(data + "\n")

except KeyboardInterrupt:
    ws.close()