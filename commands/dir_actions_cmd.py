from typing import List, Optional

from components import DirectoryUtility


def mkdir_cmd(du: Optional[DirectoryUtility] = None, args: Optional[List[str]] = None):
    if du is None:
        return ["error", "Directory utility not provided"]

    args = args or []

    if not args:
        return ["error", "Path or directory name is required"]

    success, message = du.create_directory(args[0])

    if success:
        return ["success", message]
    return ["error", message]


def rmdir_cmd(du: Optional[DirectoryUtility] = None, args: Optional[List[str]] = None):
    if du is None:
        return ["error", "Directory utility not provided"]

    args = args or []
    if not args:
        return ["error", "Path or directory name is required"]

    success, message = du.remove_directory(args[0])

    if success:
        return ["success", message]
    return ["error", message]