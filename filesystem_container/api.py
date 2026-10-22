from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from file_system_service import FileSystemService


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


# CREATE FOLDER
@app.post("/api/folders", status_code=201)
def create_folder(data: dict):
    try:
        file_system = FileSystemService(data["username"])

        file_system.create_folder(
            data["name"],
            data["path"]
        )

        return {
            "message": "Folder created"
        }

    except Exception as error:
        print(error)

        return {
            "error": "Failed to create folder"
        }


# RENAME FOLDER
@app.patch("/api/folders/rename")
def rename_folder(data: dict):
    try:
        file_system = FileSystemService(data["username"])

        file_system.rename_folder(
            data["path"],
            data["newName"]
        )

        return {
            "message": "Folder renamed"
        }

    except Exception as error:
        print(error)

        return {
            "error": "Failed to rename folder"
        }


# DELETE FOLDER
@app.delete("/api/folders")
def delete_folder(data: dict):
    try:
        file_system = FileSystemService(data["username"])

        file_system.delete_folder(
            data["path"]
        )

        return {
            "message": "Folder deleted"
        }

    except Exception as error:
        print(error)

        return {
            "error": "Failed to delete folder"
        }


# MOVE FOLDER
@app.patch("/api/folders/move")
def move_folder(data: dict):
    try:
        file_system = FileSystemService(data["username"])

        file_system.move_folder(
            data["path"],
            data["newPath"],
            data["newName"]
        )

        return {
            "message": "Folder moved"
        }

    except FileNotFoundError:
        return {
            "error": "Folder not found"
        }

    except Exception as error:
        print(error)

        return {
            "error": "Failed to move folder"
        }


# COPY FOLDER
@app.patch("/api/folders/copy")
def copy_folder(data: dict):
    try:
        file_system = FileSystemService(data["username"])

        file_system.copy_folder(
            data["path"],
            data["newPath"],
            data["newName"]
        )

        return {
            "message": "Folder copied"
        }

    except FileNotFoundError:
        return {
            "error": "Folder not found"
        }

    except Exception as error:
        print(error)

        return {
            "error": "Failed to copy folder"
        }


# READ DIRECTORY
@app.get("/api/folders")
def read_directory(
    username: str,
    name: str | None = None,
    path: str = ""
):
    try:
        file_system = FileSystemService(username)

        contents = file_system.read_directory(
            name,
            path
        )

        return contents

    except Exception as error:
        print(error)

        return {
            "error": "Failed to read directory"
        }


# CREATE FILE
@app.post("/api/files", status_code=201)
def create_file(data: dict):
    try:
        file_system = FileSystemService(data["username"])

        file_system.create_file(
            data["name"],
            data["path"]
        )

        return {
            "message": "File created"
        }

    except Exception as error:
        print(error)

        return {
            "error": "Failed to create file"
        }


# RENAME FILE
@app.patch("/api/files/rename")
def rename_file(data: dict):
    try:
        file_system = FileSystemService(data["username"])

        file_system.rename_file(
            data["path"],
            data["newName"]
        )

        return {
            "message": "File renamed"
        }

    except Exception as error:
        print(error)

        return {
            "error": "Failed to rename file"
        }


# DELETE FILE
@app.delete("/api/files")
def delete_file(data: dict):
    try:
        file_system = FileSystemService(data["username"])

        file_system.delete_file(
            data["path"]
        )

        return {
            "message": "File deleted"
        }

    except Exception as error:
        print(error)

        return {
            "error": "Failed to delete file"
        }


# SAVE FILE
@app.put("/api/files")
def save_file(data: dict):
    try:
        file_system = FileSystemService(data["username"])

        file_system.save_file(
            data["path"],
            data["content"]
        )

        return {
            "message": "File saved"
        }

    except Exception as error:
        print(error)

        return {
            "error": "Failed to save file"
        }


# MOVE FILE
@app.patch("/api/files/move")
def move_file(data: dict):
    try:
        file_system = FileSystemService(data["username"])

        file_system.move_file(
            data["path"],
            data["newPath"],
            data["newName"]
        )

        return {
            "message": "File moved"
        }

    except Exception as error:
        print(error)

        return {
            "error": "Failed to move file"
        }

@app.patch("/api/files/relocate")
def relocate_file(data: dict):
    try:
        file_system = FileSystemService(data["username"])

        file_system.relocate_file(
            data["path"],
            data["newPath"]
        )

        return {
            "message": "File relocated"
        }

    except Exception as error:
        print(error)

        return {
            "error": "Failed to relocate file"
        }

# COPY FILE
@app.patch("/api/files/copy")
def copy_file(data: dict):
    try:
        file_system = FileSystemService(data["username"])

        file_system.copy_file(
            data["path"],
            data["newPath"],
            data["newName"]
        )

        return {
            "message": "File copied"
        }

    except FileNotFoundError:
        return {
            "error": "File not found"
        }

    except Exception as error:
        print(error)

        return {
            "error": "Failed to copy file"
        }


# READ FILE
@app.get("/api/files")
def read_file(
    username: str,
    path: str
):
    try:
        if not path:
            return {
                "error": "File path is required"
            }

        file_system = FileSystemService(username)

        file = file_system.read_file(path)

        return file

    except Exception as error:
        print(error)

        return {
            "error": "Failed to read file"
        }