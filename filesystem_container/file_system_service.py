from pathlib import Path
import shutil


class FileSystemService:

    def __init__(self, username: str):
        self.root = Path("/workspace") / username
        self.root.mkdir(parents=True, exist_ok=True)

    # CREATE FOLDER
    def create_folder(
        self,
        name: str,
        parent_path: str
    ) -> None:

        folder_path = (
            self.root / parent_path / name
        ).resolve()

        if (
            folder_path != self.root
            and self.root not in folder_path.parents
        ):
            raise ValueError("Invalid path")

        folder_path.mkdir()

    # RENAME FOLDER
    def rename_folder(
        self,
        folder_path: str,
        new_name: str
    ) -> None:

        current_path = (
            self.root / folder_path
        ).resolve()

        new_path = (
            current_path.parent / new_name
        ).resolve()

        if (
            self.root not in current_path.parents
            or self.root not in new_path.parents
        ):
            raise ValueError("Invalid path")

        current_path.rename(new_path)

    # DELETE FOLDER
    def delete_folder(
        self,
        folder_path: str
    ) -> None:

        target_path = (
            self.root / folder_path
        ).resolve()

        if self.root not in target_path.parents:
            raise ValueError("Invalid path")

        shutil.rmtree(target_path)

    # MOVE FOLDER
    def move_folder(
        self,
        folder_path: str,
        new_path: str,
        new_name: str
    ) -> None:

        current_path = (
            self.root / folder_path
        ).resolve()

        target_path = (
            self.root / new_path / new_name
        ).resolve()

        if (
            self.root not in current_path.parents
            or self.root not in target_path.parents
        ):
            raise ValueError("Invalid path")

        if (
            not current_path.exists()
            or not current_path.is_dir()
        ):
            raise FileNotFoundError("Folder not found")

        current_path.rename(target_path)

    # COPY FOLDER
    def copy_folder(
        self,
        folder_path: str,
        new_path: str,
        new_name: str
    ) -> None:

        current_path = (
            self.root / folder_path
        ).resolve()

        target_path = (
            self.root / new_path / new_name
        ).resolve()

        if (
            self.root not in current_path.parents
            or self.root not in target_path.parents
        ):
            raise ValueError("Invalid path")

        if (
            not current_path.exists()
            or not current_path.is_dir()
        ):
            raise FileNotFoundError("Folder not found")

        shutil.copytree(
            current_path,
            target_path
        )

    # READ DIRECTORY
    def read_directory(
        self,
        folder_name: str | None,
        parent_path: str
    ) -> list[dict[str, str | None]]:

        folder_path = (
            (
                self.root
                / parent_path
                / folder_name
            ).resolve()
            if folder_name
            else (
                self.root / parent_path
            ).resolve()
        )

        if (
            folder_path != self.root
            and self.root not in folder_path.parents
        ):
            raise ValueError("Invalid path")

        entries = folder_path.iterdir()

        parent = (
            None
            if folder_path == self.root
            else folder_name
        )

        return [
            {
                "name": entry.name,
                "type": (
                    "directory"
                    if entry.is_dir()
                    else "file"
                ),
                "parent": parent
            }
            for entry in entries
        ]

    # CREATE FILE
    def create_file(
        self,
        file_name: str,
        parent_path: str
    ) -> None:

        file_path = (
            self.root
            / parent_path
            / file_name
        ).resolve()

        if self.root not in file_path.parents:
            raise ValueError("Invalid path")

        file_path.write_text("")

    # RENAME FILE
    def rename_file(
        self,
        file_path: str,
        new_name: str
    ) -> None:

        current_path = (
            self.root / file_path
        ).resolve()

        new_path = (
            current_path.parent / new_name
        ).resolve()

        if (
            self.root not in current_path.parents
            or self.root not in new_path.parents
        ):
            raise ValueError("Invalid path")

        current_path.rename(new_path)

    # DELETE FILE
    def delete_file(
        self,
        file_path: str
    ) -> None:

        target_path = (
            self.root / file_path
        ).resolve()

        if self.root not in target_path.parents:
            raise ValueError("Invalid path")

        target_path.unlink()

    # SAVE FILE
    def save_file(
        self,
        file_path: str,
        content: str
    ) -> None:

        target_path = (
            self.root / file_path
        ).resolve()

        if self.root not in target_path.parents:
            raise ValueError("Invalid path")

        target_path.write_text(
            content,
            encoding="utf-8"
        )

    # MOVE FILE
    def move_file(
        self,
        file_path: str,
        new_path: str,
        new_name: str
    ) -> None:

        current_path = (
            self.root / file_path
        ).resolve()

        target_path = (
            self.root
            / new_path
            / new_name
        ).resolve()

        if (
            self.root not in current_path.parents
            or self.root not in target_path.parents
        ):
            raise ValueError("Invalid path")

        current_path.rename(target_path)
        
    def relocate_file(
      self,
      file_path: str,
      new_path: str
    ) -> None:

      current_path = (
        self.root / file_path
      ).resolve()

      target_path = (
        self.root
        / new_path
        / current_path.name
      ).resolve()

      if (
        self.root not in current_path.parents
        or self.root not in target_path.parents
      ):
        raise ValueError("Invalid path")

      current_path.rename(target_path)

    # COPY FILE
    def copy_file(
        self,
        file_path: str,
        new_path: str,
        new_name: str
    ) -> None:

        current_path = (
            self.root / file_path
        ).resolve()

        target_path = (
            self.root
            / new_path
            / new_name
        ).resolve()

        if (
            self.root not in current_path.parents
            or self.root not in target_path.parents
        ):
            raise ValueError("Invalid path")

        if (
            not current_path.exists()
            or not current_path.is_file()
        ):
            raise FileNotFoundError("File not found")

        shutil.copy2(
            current_path,
            target_path
        )

    # READ FILE
    def read_file(
        self,
        file_path: str
    ) -> dict[str, str]:

        target_path = (
            self.root / file_path
        ).resolve()

        if self.root not in target_path.parents:
            raise ValueError("Invalid path")

        content = target_path.read_text(
            encoding="utf-8"
        )

        return {
            "name": target_path.name,
            "type": "file",
            "parent": target_path.parent.name,
            "content": content
        }