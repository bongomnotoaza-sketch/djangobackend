from .main_service import MainService


class DirectoryBuilderService:

    EXCLUDED_DIRECTORIES = {
        ".venv",
        "venv",
        "env",
        "__pycache__",
        ".git",
        "node_modules",
    }

    def __init__(self):
        self.main_service = MainService()

    def build_directory_structure(
        self,
        username: str,
        folder_name: str | None = None,
        parent_path: str = ""
    ) -> dict[str, dict]:

        structure = {}

        entries = self.main_service.read_directory(
            username=username,
            name=folder_name,
            path=parent_path
        )

        current_path = (
            f"{parent_path}/{folder_name}"
            if folder_name
            else parent_path
        )

        for entry in entries:

            name = entry["name"]
            entry_type = entry["type"]

            # Ignore virtual environments and generated directories
            if (
                entry_type == "directory"
                and name in self.EXCLUDED_DIRECTORIES
            ):
                continue

            entry_path = (
                f"{current_path}/{name}"
                if current_path
                else name
            )

            if entry_type == "directory":

                structure[entry_path] = {
                    "type": "folder"
                }

                nested_structure = self.build_directory_structure(
                    username=username,
                    folder_name=name,
                    parent_path=current_path
                )

                structure.update(nested_structure)

            elif entry_type == "file":

                file_data = self.main_service.read_file(
                    username=username,
                    path=entry_path
                )

                if "content" not in file_data:
                   print("❌ FILE WITHOUT CONTENT")
                   print("Path:", entry_path)
                   print("File data:", file_data)
                   continue

                content = file_data["content"]

                structure[entry_path] = {
                    "type": "file",
                    "name": file_data["name"],
                    "content": content,
                    "size": len(content)
                }

        return structure