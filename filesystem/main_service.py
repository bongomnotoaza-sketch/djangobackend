
import requests


class MainService:

    def create_folder(
        self,
        username: str,
        name: str,
        path: str
    ):
        url = f"http://{username}-files:3005/api/folders"

        response = requests.post(
            url,
            json={
                "username": username,
                "name": name,
                "path": path
            }
        )

        return response.json()

    def rename_folder(
        self,
        username: str,
        path: str,
        new_name: str
    ):
        url = f"http://{username}-files:3005/api/folders/rename"

        response = requests.patch(
            url,
            json={
                "username": username,
                "path": path,
                "newName": new_name
            }
        )

        return response.json()

    def delete_folder(
        self,
        username: str,
        path: str
    ):
        url = f"http://{username}-files:3005/api/folders"

        response = requests.delete(
            url,
            json={
                "username": username,
                "path": path
            }
        )

        return response.json()

    def move_folder(
        self,
        username: str,
        path: str,
        new_path: str,
        new_name: str
    ):
        url = f"http://{username}-files:3005/api/folders/move"

        response = requests.patch(
            url,
            json={
                "username": username,
                "path": path,
                "newPath": new_path,
                "newName": new_name
            }
        )

        return response.json()

    def copy_folder(
        self,
        username: str,
        path: str,
        new_path: str,
        new_name: str
    ):
        url = f"http://{username}-files:3005/api/folders/copy"

        response = requests.patch(
            url,
            json={
                "username": username,
                "path": path,
                "newPath": new_path,
                "newName": new_name
            }
        )

        return response.json()

    def create_file(
        self,
        username: str,
        name: str,
        path: str
    ):
        url = f"http://{username}-files:3005/api/files"

        response = requests.post(
            url,
            json={
                "username": username,
                "name": name,
                "path": path
            }
        )

        return response.json()

    def rename_file(
        self,
        username: str,
        path: str,
        new_name: str
    ):
        url = f"http://{username}-files:3005/api/files/rename"

        response = requests.patch(
            url,
            json={
                "username": username,
                "path": path,
                "newName": new_name
            }
        )

        return response.json()

    def delete_file(
        self,
        username: str,
        path: str
    ):
        url = f"http://{username}-files:3005/api/files"

        response = requests.delete(
            url,
            json={
                "username": username,
                "path": path
            }
        )

        return response.json()

    def save_file(
        self,
        username: str,
        path: str,
        content: str
    ):
        url = f"http://{username}-files:3005/api/files"

        response = requests.put(
            url,
            json={
                "username": username,
                "path": path,
                "content": content
            }
        )

        return response.json()

    def save_as(
        self,
        username: str,
        path: str,
        new_path: str,
        new_name: str
    ):
        url = f"http://{username}-files:3005/api/files/relocate"

        response = requests.patch(
            url,
            json={
                "username": username,
                "path": path,
                "newPath": new_path,
                "newName": new_name
            }
        )

        return response.json()
    
    def move_file(
      self,
      username: str,
      path: str,
      new_path: str
    ):
      url = f"http://{username}-files:3005/api/files/relocate"

      response = requests.patch(
        url,
        json={
            "username": username,
            "path": path,
            "newPath": new_path
        }
      )

      return response.json()

    def copy_file(
        self,
        username: str,
        path: str,
        new_path: str,
        new_name: str
    ):
        url = f"http://{username}-files:3005/api/files/copy"

        response = requests.patch(
            url,
            json={
                "username": username,
                "path": path,
                "newPath": new_path,
                "newName": new_name
            }
        )

        return response.json()

    def read_directory(
        self,
        username: str,
        name: str | None = None,
        path: str = ""
    ):
        url = f"http://{username}-files:3005/api/folders"

        params = {
            "username": username,
            "path": path
        }

        if name is not None:
            params["name"] = name

        response = requests.get(
            url,
            params=params
        )

        return response.json()

    def read_file(
        self,
        username: str,
        path: str
    ):
        url = f"http://{username}-files:3005/api/files"

        response = requests.get(
            url,
            params={
                "username": username,
                "path": path
            }
        )

        return response.json()
