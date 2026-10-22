from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from api import router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


app.include_router(router, prefix="/api")


PORT = 3005


if __name__ == "__main__":
    print(f"Filesystem service running on port {PORT}")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=PORT
    )