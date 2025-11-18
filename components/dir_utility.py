import os
import stat
import time
from datetime import datetime
import shutil


class DirectoryUtility:
    def __init__(self, current_directory: str):
        self.current_directory = current_directory

    def _resolve_path(self, path: str) -> str:
        if not path:
            return self.current_directory
        if os.path.isabs(path):
            return os.path.abspath(path)
        return os.path.abspath(os.path.join(self.current_directory, path))

    def list_directory(self, type_output: str = "ls"):
        """
        type_output options:
        - "ls": простой список (как ls)
        - "ll": подробный список (как ll или ls -l)
        - "la": все файлы включая скрытые (как ls -a)
        - "lla": все файлы подробно (как ll -a или ls -la)
        """
        try:
            if type_output == "ls":
                return self._format_ls()
            elif type_output == "ll":
                return self._format_ll()
            elif type_output == "la":
                return self._format_la()
            elif type_output == "lla":
                return self._format_lla()
            else:
                raise ValueError(f"Invalid type_output: {type_output}")
        except Exception as e:
            return f"Error: {e}"

    def _get_file_info(self, filename):
        """Получает подробную информацию о файле"""
        filepath = os.path.join(self.current_directory, filename)
        stat_info = os.stat(filepath)

        # Права доступа
        permissions = stat.filemode(stat_info.st_mode)

        # Количество ссылок
        nlinks = stat_info.st_nlink

        # Владелец и группа (попробуем получить имена)
        try:
            import pwd

            owner = pwd.getpwuid(stat_info.st_uid).pw_name
        except (ImportError, KeyError):
            owner = str(stat_info.st_uid)

        try:
            import grp

            group = grp.getgrgid(stat_info.st_gid).gr_name
        except (ImportError, KeyError):
            group = str(stat_info.st_gid)

        # Размер файла
        size = stat_info.st_size

        # Время изменения
        mtime = datetime.fromtimestamp(stat_info.st_mtime)
        mtime_str = mtime.strftime("%b %d %H:%M")

        # Тип файла (символ)
        file_type = self._get_file_type(stat_info.st_mode, filename)

        return {
            "permissions": permissions,
            "nlinks": nlinks,
            "owner": owner,
            "group": group,
            "size": size,
            "mtime": mtime_str,
            "filename": filename,
            "file_type": file_type,
        }

    def _get_file_type(self, st_mode, filename):
        """Определяет тип файла"""
        if stat.S_ISDIR(st_mode):
            return "d"
        elif stat.S_ISLNK(st_mode):
            return "l"
        elif stat.S_ISREG(st_mode):
            return "-"
        elif stat.S_ISFIFO(st_mode):
            return "p"
        elif stat.S_ISSOCK(st_mode):
            return "s"
        elif stat.S_ISCHR(st_mode):
            return "c"
        elif stat.S_ISBLK(st_mode):
            return "b"
        else:
            return "?"

    def _format_ls(self):
        """Форматирование как ls - простой список"""
        files = [f for f in os.listdir(self.current_directory) if not f.startswith(".")]
        return "\n".join(self._format_with_icon(f) for f in files)

    def _format_ll(self):
        """Форматирование как ll - подробный список без скрытых файлов"""
        files = [f for f in os.listdir(self.current_directory) if not f.startswith(".")]
        return self._format_detailed_list(files)

    def _format_la(self):
        """Форматирование как ls -a - все файлы простым списком"""
        files = os.listdir(self.current_directory)
        return "\n".join(self._format_with_icon(f) for f in files)

    def _format_lla(self):
        """Форматирование как ll -a - все файлы подробно"""
        files = os.listdir(self.current_directory)
        return self._format_detailed_list(files)

    def _format_with_icon(self, filename: str) -> str:
        icon = self._get_icon(filename)
        return f"{icon} {filename}"

    def _get_icon(self, filename: str) -> str:
        filepath = os.path.join(self.current_directory, filename)
        try:
            if os.path.isdir(filepath):
                return "📁"
            if os.path.islink(filepath):
                return "🔗"
            if os.path.isfile(filepath):
                _, ext = os.path.splitext(filename.lower())
                if ext in {".py", ".sh"}:
                    return "🐍"
                if ext in {".txt", ".md"}:
                    return "📄"
                if ext in {".jpg", ".png", ".gif", ".jpeg", ".webp"}:
                    return "🖼️"
                if ext in {".zip", ".tar", ".gz", ".rar"}:
                    return "🗜️"
                return "📦"
        except OSError:
            pass
        return "❓"

    def _format_detailed_list(self, files):
        """Форматирует подробный список файлов"""
        if not files:
            return ""

        # Получаем информацию о всех файлах
        file_infos = []
        total_blocks = 0

        for filename in files:
            info = self._get_file_info(filename)
            file_infos.append(info)
            total_blocks += self._calculate_blocks(info["size"])

        # Форматируем вывод
        lines = [f"total {total_blocks}"]

        for info in file_infos:
            icon = self._get_icon(info["filename"])
            line = (
                f"{info['permissions']} {info['nlinks']:>2} {info['owner']:>8} {info['group']:>8} "
                f"{info['size']:>8} {info['mtime']} {icon} {info['filename']}"
            )
            lines.append(line)

        return "\n".join(lines)

    def _calculate_blocks(self, size):
        """Вычисляет количество блоков (как в ls -l)"""
        # В Linux обычно 1 блок = 512 байт
        block_size = 512
        return (size + block_size - 1) // block_size

    def get_current_directory(self):
        """Возвращает текущую директорию"""
        return self.current_directory

    def change_directory(self, new_path):
        """Меняет текущую директорию"""
        if not new_path:
            new_path = os.path.expanduser("~")  # Домашняя директория

        new_abs_path = self._resolve_path(new_path)

        if os.path.exists(new_abs_path) and os.path.isdir(new_abs_path):
            self.current_directory = new_abs_path
            return True
        else:
            return False

    def create_directory(self, new_path):
        """Создает новую директорию"""
        if not new_path:
            return False, "Path is required"

        new_abs_path = self._resolve_path(new_path)

        if os.path.exists(new_abs_path):
            return False, f"Directory already exists: {new_abs_path}"

        try:
            os.makedirs(new_abs_path, exist_ok=False)
            return True, f"Directory created: {new_abs_path}"
        except OSError as e:
            return False, f"Failed to create directory: {e}"

    def remove_directory(self, path, recursive: bool = True):
        """Удаляет директорию (по умолчанию рекурсивно)."""
        if not path:
            return False, "Path is required"

        target_path = self._resolve_path(path)

        if not os.path.exists(target_path):
            return False, f"Directory does not exist: {target_path}"

        if not os.path.isdir(target_path):
            return False, f"Not a directory: {target_path}"

        try:
            if recursive:
                shutil.rmtree(target_path)
            else:
                os.rmdir(target_path)
            return True, f"Directory removed: {target_path}"
        except OSError as e:
            return False, f"Failed to remove directory: {e}"
