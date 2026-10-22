from pathlib import Path


class FileSystemService:

    def __init__(self):
        self.root = Path("/tmp/filesystem-test")

    def create_folder(self, name: str, parent_path: str) -> None:
        folder_path = (self.root / parent_path / name).resolve()

        if folder_path != self.root and self.root not in folder_path.parents:
            raise ValueError("Invalid path")

        folder_path.mkdir()

    def rename_folder(self, folder_path: str, new_name: str) -> None:

        current_path = (self.root / folder_path).resolve()

        new_path = current_path.parent / new_name

        # Prevent access outside the root directory
        if (
            self.root not in current_path.parents
            or self.root not in new_path.resolve().parents
        ):
            raise ValueError("Invalid path")

        current_path.rename(new_path)
        
    def delete_folder(self, folder_path: str) -> None:
      target_path = (self.root / folder_path).resolve()

      if self.root not in target_path.parents:
        raise ValueError("Invalid path")

      import shutil
      shutil.rmtree(target_path)
      
    def create_file(self, file_name: str, parent_path: str) -> None:
      file_path = (self.root / parent_path / file_name).resolve()

      if self.root not in file_path.parents:
        raise ValueError("Invalid path")

      file_path.write_text("")
      
    def rename_file(self, file_path: str, new_name: str) -> None:
      current_path = (self.root / file_path).resolve()

      new_path = current_path.parent / new_name
      
    def delete_file(self, file_path: str) -> None:
      target_path = (self.root / file_path).resolve()

      if self.root not in target_path.parents:
        raise ValueError("Invalid path")

      target_path.unlink()
      
    def save_file(self, file_path: str, content: str) -> None:
      target_path = (self.root / file_path).resolve()

      if self.root not in target_path.parents:
        raise ValueError("Invalid path")

      target_path.write_text(content, encoding="utf-8")
      
    def move_file(
      self,
      file_path: str,
      new_path: str,
      new_name: str
    ) -> None:
      current_path = (self.root / file_path).resolve()
      target_path = (self.root / new_path / new_name).resolve()

      if (
        self.root not in current_path.parents
        or self.root not in target_path.parents
      ):
        raise ValueError("Invalid path")

      current_path.rename(target_path)