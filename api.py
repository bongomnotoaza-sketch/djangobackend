from fastapi import FastAPI
from file_system_service import FileSystemService

app = FastAPI()

file_system = FileSystemService()


@app.post("/folders", status_code=201)
def create_folder(data: dict):
    try:
        file_system.create_folder(
            data["name"],
            data["path"]
        )

        return {
            "message": "Folder created"
        }

    except Exception:
        return {
            "error": "Failed to create folder"
        }
        
@app.patch("/folders/rename")
def rename_folder(data: dict):
    try:
        file_system.rename_folder(
            data["path"],
            data["newName"]
        )

        return {
            "message": "Folder renamed"
        }

    except Exception:
        return {
            "error": "Failed to rename folder"
        }
        
@app.delete("/folders")
def delete_folder(data: dict):
    try:
        file_system.delete_folder(data["path"])

        return {
            "message": "Folder deleted"
        }

    except Exception:
        return {
            "error": "Failed to delete folder"
        }
        
@app.post("/files", status_code=201)
def create_file(data: dict):
    try:
        file_system.create_file(
            data["name"],
            data["path"]
        )

        return {
            "message": "File created"
        }

    except Exception:
        return {
            "error": "Failed to create file"
        }
        
@app.patch("/files/rename")
def rename_file(data: dict):
    try:
        file_system.rename_file(
            data["path"],
            data["newName"]
        )

        return {
            "message": "File renamed"
        }

    except Exception:
        return {
            "error": "Failed to rename file"
        }
        
@app.delete("/files")
def delete_file(data: dict):
    try:
        file_system.delete_file(data["path"])

        return {
            "message": "File deleted"
        }

    except Exception:
        return {
            "error": "Failed to delete file"
        }
        
@app.put("/files")
def save_file(data: dict):
    try:
        file_system.save_file(
            data["path"],
            data["content"]
        )

        return {
            "message": "File saved"
        }

    except Exception:
        return {
            "error": "Failed to save file"
        }
        
@app.patch("/files/move")
def move_file(data: dict):
    try:
        file_system.move_file(
            data["path"],
            data["newPath"],
            data["newName"]
        )

        return {
            "message": "File moved"
        }

    except Exception:
        return {
            "error": "Failed to move file"
        }
        
@app.get("/folders")
def read_directory(name: str | None = None, path: str = ""):
    try:
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
        
@app.get("/files")
def read_file(path: str | None = None):
    try:
        if not path:
            return {
                "error": "File path is required"
            }

        file = file_system.read_file(path)

        return file

    except Exception as error:
        print(error)

        return {
            "error": "Failed to read file"
        }