import asyncio
import docker
import websockets
import sys

CONTAINER_NAME = "MNOLIB641-ubuntu"

async def terminal(websocket):
    print(f"New client connected: {websocket.remote_address}")
    
    try:
        # Get Docker client
        client = docker.from_env()
        
        # Get the container
        try:
            container = client.containers.get(CONTAINER_NAME)
            print(f"Found container: {CONTAINER_NAME}")
        except docker.errors.NotFound:
            error_msg = f"Container {CONTAINER_NAME} not found"
            print(error_msg)
            await websocket.send(f"\r\n\x1b[1;31m{error_msg}\x1b[0m\r\n")
            await websocket.close()
            return
        
        # Ensure container is running
        if container.status != 'running':
            print(f"Container is {container.status}, starting it...")
            container.start()
            await asyncio.sleep(2)  # Wait for container to start
        
        # Create exec instance - removed 'detach' parameter
        print("Creating exec instance...")
        exec_instance = client.api.exec_create(
            container.id,
            cmd=["/bin/bash"],
            stdin=True,
            stdout=True,
            stderr=True,
            tty=True,
            environment=["TERM=xterm-256color"]
        )
        
        print(f"Exec instance created: {exec_instance['Id']}")
        
        # Start exec with socket
        exec_socket = client.api.exec_start(
            exec_instance["Id"],
            socket=True,
            demux=False,
        )
        
        print("Exec socket created, starting communication...")
        
        # Send initial message to client
        await websocket.send("\r\n\x1b[1;32mConnected to Docker container\x1b[0m\r\n")
        await websocket.send("\x1b[1;33mType 'exit' to disconnect\x1b[0m\r\n")
        await websocket.send("\r\n$ ")
        
        loop = asyncio.get_running_loop()
        
        async def read_terminal():
            """Read from Docker exec socket and send to WebSocket"""
            try:
                while True:
                    # Read data from exec socket
                    data = await loop.run_in_executor(
                        None,
                        exec_socket.recv,
                        4096
                    )
                    
                    if not data:
                        print("No data received from exec socket")
                        break
                    
                    # Send to WebSocket
                    try:
                        # Handle both bytes and string responses
                        if isinstance(data, bytes):
                            await websocket.send(data.decode('utf-8', errors='replace'))
                        else:
                            await websocket.send(str(data))
                    except websockets.exceptions.ConnectionClosed:
                        print("WebSocket closed during read")
                        break
                        
            except Exception as e:
                print(f"Error reading from terminal: {e}")
            
            print("read_terminal finished")
        
        async def write_terminal():
            """Read from WebSocket and send to Docker exec socket"""
            try:
                async for message in websocket:
                    try:
                        # Ensure we send bytes
                        if isinstance(message, str):
                            message_bytes = message.encode('utf-8')
                        else:
                            message_bytes = message
                        
                        # Send to exec socket
                        await loop.run_in_executor(
                            None,
                            exec_socket.send,
                            message_bytes
                        )
                    except Exception as e:
                        print(f"Error writing to terminal: {e}")
                        break
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket closed during write")
            except Exception as e:
                print(f"write_terminal error: {e}")
            
            print("write_terminal finished")
        
        # Run both tasks concurrently
        try:
            await asyncio.gather(
                read_terminal(),
                write_terminal()
            )
        except Exception as e:
            print(f"Gather error: {e}")
            
    except docker.errors.APIError as e:
        error_msg = f"Docker API Error: {str(e)}"
        print(error_msg)
        try:
            await websocket.send(f"\r\n\x1b[1;31m{error_msg}\x1b[0m\r\n")
        except:
            pass
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        try:
            if 'exec_socket' in locals():
                exec_socket.close()
        except:
            pass
        print(f"Client disconnected: {websocket.remote_address}")

async def main():
    # Check if Docker is available
    try:
        client = docker.from_env()
        client.ping()
        print("Docker daemon is running")
    except Exception as e:
        print(f"Error connecting to Docker: {e}")
        sys.exit(1)
    
    # Start WebSocket server
    async with websockets.serve(
        terminal,
        "127.0.0.1",
        8764,
        ping_interval=30,
        ping_timeout=10,
        close_timeout=5,
        max_queue=32,
    ):
        print("Terminal WebSocket running on ws://127.0.0.1:8764")
        print(f"Using container: {CONTAINER_NAME}")
        print("Press Ctrl+C to stop")
        
        try:
            await asyncio.Future()  # Run forever
        except KeyboardInterrupt:
            print("\nShutting down...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped")