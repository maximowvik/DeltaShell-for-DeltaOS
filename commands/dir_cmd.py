from typing import List, Optional

from components import DirectoryUtility


def ls_cmd(du: Optional[DirectoryUtility] = None, args: Optional[List[str]] = None):
    if du is None:
        return ["error", "Directory utility not provided"]

    args = args or []

    # Определяем тип вывода на основе аргументов
    output_type = "ls"
    if "-l" in args and "-a" in args:
        output_type = "lla"
    elif "-l" in args:
        output_type = "ll"
    elif "-a" in args:
        output_type = "la"

    return ["success", du.list_directory(output_type)]


def cd_cmd(du: Optional[DirectoryUtility] = None, args: Optional[List[str]] = None):
    if du is None:
        return ["error", "Directory utility not provided"]

    args = args or []

    path = args[0] if args else ""

    if du.change_directory(path):
        return ["success", f"Changed to {du.get_current_directory()}"]
    else:
        return ["error", f"Directory not found: {path}"]


def pwd_cmd(du: Optional[DirectoryUtility] = None, args: Optional[List[str]] = None):
    if du is None:
        return ["error", "Directory utility not provided"]

    return ["success", du.get_current_directory()]
