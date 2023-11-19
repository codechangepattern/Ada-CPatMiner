from pathlib import Path


class FileIO:

    @staticmethod
    def get_simple_file_name(file_name: str) -> str:
        return Path(file_name).stem
