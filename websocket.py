#!/usr/bin/env python3
"""
WebSocket IDE Server - Full C++ Support
Compiles and runs C++ code with g++/clang++
"""

import asyncio
import json
import os
import shutil
import sys
import tempfile
import platform
import subprocess
import websockets

# ---------------------------------------------------------------------------
# Per-language configuration
#
# Each language gets its own temp directory (not just a temp file) because
# compiled languages need room for the compiler's output (a .class file, an
# executable, etc). "filename" must match what that language's compiler
# expects (e.g. Java requires the file to be named after its public class).
#
# "compile_cmd" is None for languages that run directly from source.
# Both commands are functions of (dir, file_path) -> list[str] argv.
# ---------------------------------------------------------------------------
LANGUAGE_CONFIGS = {
    "python": {
        "display_name": "Python",
        "filename": "script.py",
        "compile_cmd": None,
        "run_cmd": lambda d, f: [sys.executable, "-u", f],
    },
    "javascript": {
        "display_name": "JavaScript",
        "filename": "script.js",
        "compile_cmd": None,
        "run_cmd": lambda d, f: ["node", f],
    },
    "java": {
        "display_name": "Java",
        "filename": "Main.java",
        "compile_cmd": lambda d, f: ["javac", f],
        "run_cmd": lambda d, f: ["java", "-cp", d, "Main"],
    },
    "cpp": {
        "display_name": "C++",
        "filename": "main.cpp",
        "compile_cmd": lambda d, f: ["g++", "-std=c++17", "-Wall", "-O2", f, "-o", os.path.join(d, "main")],
        "run_cmd": lambda d, f: [os.path.join(d, "main")],
    },
    "c": {
        "display_name": "C",
        "filename": "main.c",
        "compile_cmd": lambda d, f: ["gcc", "-std=c11", "-Wall", "-O2", f, "-o", os.path.join(d, "main")],
        "run_cmd": lambda d, f: [os.path.join(d, "main")],
    },
    "csharp": {
        "display_name": "C#",
        "filename": "Program.cs",
        "compile_cmd": lambda d, f: ["csc", f],
        "run_cmd": lambda d, f: ["mono", os.path.join(d, "Program.exe")],
    },
    "go": {
        "display_name": "Go",
        "filename": "main.go",
        "compile_cmd": lambda d, f: ["go", "build", "-o", os.path.join(d, "main"), f],
        "run_cmd": lambda d, f: [os.path.join(d, "main")],
    },
    "rust": {
        "display_name": "Rust",
        "filename": "main.rs",
        "compile_cmd": lambda d, f: ["rustc", f, "-o", os.path.join(d, "main")],
        "run_cmd": lambda d, f: [os.path.join(d, "main")],
    },
}

# ---------------------------------------------------------------------------
# Small helper for sending JSON messages back to the client
# ---------------------------------------------------------------------------
async def send_json(websocket, payload):
    try:
        await websocket.send(json.dumps(payload))
    except websockets.ConnectionClosed:
        pass


# ---------------------------------------------------------------------------
# Streaming helpers
# ---------------------------------------------------------------------------
async def stream_stdout(process, websocket):
    """Continuously read process.stdout and forward output as soon as it appears.

    Reads raw chunks (not lines) because an input() prompt like "Name: " has
    no trailing newline and would otherwise never be flushed to the client.
    If a chunk doesn't end in a newline, we treat it as a likely input
    prompt and tell the frontend to show its stdin box.
    """
    try:
        while True:
            chunk = await process.stdout.read(1024)
            if not chunk:
                break
            text = chunk.decode(errors="replace")
            await send_json(websocket, {"type": "stdout", "data": text})
            if not text.endswith("\n"):
                await send_json(websocket, {"type": "stdin_request"})
    except Exception as e:
        await send_json(websocket, {"type": "stderr", "data": f"stdout stream error: {e}"})


async def stream_stderr(process, websocket):
    """Continuously read process.stderr and forward output as soon as it appears."""
    try:
        while True:
            chunk = await process.stderr.read(1024)
            if not chunk:
                break
            await send_json(websocket, {
                "type": "stderr",
                "data": chunk.decode(errors="replace")
            })
    except Exception as e:
        await send_json(websocket, {"type": "stderr", "data": f"stderr stream error: {e}"})


# ---------------------------------------------------------------------------
# Process lifecycle helpers
# ---------------------------------------------------------------------------
async def monitor_process(process, websocket, state):
    """Wait for the process to exit, report the exit code, then clean up."""
    returncode = await process.wait()

    # Let the stdout/stderr readers finish flushing whatever is left.
    tasks = [t for t in (state.get("stdout_task"), state.get("stderr_task")) if t is not None]
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

    await send_json(websocket, {"type": "exit", "exitCode": returncode})
    cleanup_process(state)


def cleanup_process(state):
    """Delete the temp directory and reset the per-connection process state."""
    tmp_dir = state.get("tmp_dir")
    if tmp_dir and os.path.isdir(tmp_dir):
        shutil.rmtree(tmp_dir, ignore_errors=True)

    state["process"] = None
    state["tmp_dir"] = None
    state["stdout_task"] = None
    state["stderr_task"] = None
    state["monitor_task"] = None


async def compile_code(dir_path, file_path, config, websocket):
    """Run the language's compile step, if it has one.

    Returns True if it's fine to proceed to running the program (either
    compilation succeeded, or there was nothing to compile). Returns False
    if compilation failed, after reporting the compiler's stderr/stdout.
    """
    compile_cmd = config["compile_cmd"]
    if compile_cmd is None:
        return True

    argv = compile_cmd(dir_path, file_path)
    try:
        proc = await asyncio.create_subprocess_exec(
            *argv,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=dir_path,
        )
        stdout, stderr = await proc.communicate()
    except FileNotFoundError:
        await send_json(websocket, {
            "type": "stderr",
            "data": f"Compiler not found for this language: {argv[0]}\nPlease install the required compiler.\n"
        })
        return False
    except Exception as e:
        await send_json(websocket, {"type": "stderr", "data": f"Compilation error: {e}\n"})
        return False

    if proc.returncode != 0:
        output = (stderr or stdout).decode(errors="replace")
        await send_json(websocket, {"type": "stderr", "data": "Compilation failed:\n" + output + "\n"})
        await send_json(websocket, {"type": "exit", "exitCode": proc.returncode})
        return False

    # If compilation succeeded but produced any stderr (warnings), show them
    if stderr:
        warning_text = stderr.decode(errors="replace")
        if warning_text.strip():
            await send_json(websocket, {"type": "stderr", "data": "Compilation warnings:\n" + warning_text + "\n"})

    return True


async def run_code_process(websocket, code, language, state):
    """Write the received code to a temp dir and run/compile+run it."""
    if state.get("process") is not None and state["process"].returncode is None:
        await send_json(websocket, {"type": "status", "data": "A script is already running. Stop it first.\n"})
        return

    config = LANGUAGE_CONFIGS.get(language)
    if config is None:
        await send_json(websocket, {
            "type": "stderr",
            "data": f"Unsupported language: {language}\n"
        })
        return

    tmp_dir = tempfile.mkdtemp(prefix="ws_ide_")
    state["tmp_dir"] = tmp_dir

    try:
        file_path = os.path.join(tmp_dir, config["filename"])
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code)

        # Compile if needed
        if not await compile_code(tmp_dir, file_path, config, websocket):
            cleanup_process(state)
            return

        # Run the program
        argv = config["run_cmd"](tmp_dir, file_path)
        
        # Make executable on Unix systems
        if platform.system() != "Windows" and language in ["cpp", "c", "go", "rust"]:
            try:
                os.chmod(argv[0], 0o755)
            except Exception:
                pass

        env = {**os.environ, "PYTHONUNBUFFERED": "1"}
        process = await asyncio.create_subprocess_exec(
            *argv,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=tmp_dir,
            env=env,
        )
        state["process"] = process

        state["stdout_task"] = asyncio.create_task(stream_stdout(process, websocket))
        state["stderr_task"] = asyncio.create_task(stream_stderr(process, websocket))
        state["monitor_task"] = asyncio.create_task(monitor_process(process, websocket, state))

    except FileNotFoundError as e:
        await send_json(websocket, {"type": "stderr", "data": f"Runtime not found: {e}\n"})
        cleanup_process(state)
    except Exception as e:
        await send_json(websocket, {"type": "stderr", "data": f"Failed to start process: {e}\n"})
        cleanup_process(state)


async def handle_stdin(process, data):
    """Forward stdin data from the client to the running process."""
    if process is None or process.returncode is not None or process.stdin is None:
        return
    try:
        process.stdin.write((data + "\n").encode())
        await process.stdin.drain()
    except Exception:
        # Process may have already closed stdin (e.g. it didn't call input()).
        pass


async def stop_process(state, websocket):
    """Terminate (or kill) the running process gracefully."""
    process = state.get("process")
    if process is None or process.returncode is not None:
        await send_json(websocket, {"type": "status", "data": "No script is currently running.\n"})
        return

    try:
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=3)
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
    except ProcessLookupError:
        pass

    await send_json(websocket, {"type": "status", "data": "Execution stopped.\n"})
    # monitor_process (already running) will detect the exit, send the
    # "exit" message, and perform cleanup on its own.


async def send_languages(websocket):
    """Send the list of supported languages to the client."""
    languages = [
        {
            "id": lang_id,
            "name": config["display_name"]
        }
        for lang_id, config in LANGUAGE_CONFIGS.items()
    ]
    await send_json(websocket, {
        "type": "languages",
        "languages": languages
    })


# ---------------------------------------------------------------------------
# WebSocket handler
# ---------------------------------------------------------------------------
async def handler(websocket):
    print(f"Client connected from {websocket.remote_address}")

    state = {
        "process": None,
        "tmp_dir": None,
        "stdout_task": None,
        "stderr_task": None,
        "monitor_task": None,
    }

    try:
        async for message in websocket:
            try:
                msg = json.loads(message)
            except json.JSONDecodeError:
                await send_json(websocket, {"type": "stderr", "data": "Invalid JSON received.\n"})
                continue

            msg_type = msg.get("type")

            try:
                if msg_type == "get_languages":
                    await send_languages(websocket)

                elif msg_type == "run":
                    code = msg.get("code", "")
                    language = msg.get("language", "python")
                    await send_json(websocket, {"type": "status", "data": f"Running {language} code...\n"})
                    await run_code_process(websocket, code, language, state)

                elif msg_type == "stdin":
                    await handle_stdin(state.get("process"), msg.get("data", ""))

                elif msg_type == "stop":
                    await stop_process(state, websocket)

                elif msg_type == "ping":
                    await send_json(websocket, {"type": "status", "data": "pong\n"})

                else:
                    await send_json(websocket, {
                        "type": "stderr",
                        "data": f"Unknown message type: {msg_type}\n"
                    })

            except Exception as e:
                await send_json(websocket, {"type": "stderr", "data": f"Error handling message: {e}\n"})

    except websockets.ConnectionClosed:
        print("Client disconnected")

    finally:
        # If the client disconnects while a script is still running, kill it
        # and clean up the temp file so nothing is left behind.
        process = state.get("process")
        if process is not None and process.returncode is None:
            try:
                process.kill()
            except Exception:
                pass
        cleanup_process(state)


async def main():
    # Check for required compilers
    print("=" * 60)
    print("WebSocket IDE Server")
    print("=" * 60)
    
    # Check compilers
    compilers = {
        "g++": "C++",
        "gcc": "C",
        "javac": "Java",
        "node": "JavaScript",
        "go": "Go",
        "rustc": "Rust",
        "csc": "C#",
        "mono": "Mono (C# runtime)"
    }
    
    print("\nChecking for installed compilers/runtimes:")
    missing = []
    for cmd, name in compilers.items():
        if shutil.which(cmd):
            print(f"  ✅ {name} ({cmd})")
        else:
            print(f"  ❌ {name} ({cmd}) - NOT INSTALLED")
            missing.append(cmd)
    
    if missing:
        print(f"\n⚠️  Missing compilers: {', '.join(missing)}")
        print("   Install them using your package manager.")
        print("   For Ubuntu/Debian: sudo apt install g++ gcc default-jdk nodejs golang rustc mono-mcs")
        print("   For macOS: brew install gcc openjdk node go rust mono")
    
    print("\nStarting WebSocket server on 0.0.0.0:8765...")
    print("Connect your browser to ws://172.20.10.6:8765 (or your IP)")
    print("Press Ctrl+C to stop\n")
    
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # Run forever


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped.")
        sys.exit(0)