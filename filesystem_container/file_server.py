import uvicorn

from api import app


PORT = 3005


if __name__ == "__main__":
    print(f"Filesystem service running on port {PORT}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT
    )