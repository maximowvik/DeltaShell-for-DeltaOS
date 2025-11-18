import shutil
import subprocess
from typing import List

from components import dir_utility


def isInteractiveCommand(command: str) -> bool:
    """
    Проверяет, является ли команда интерактивной или требует прямого вывода в терминал.

    Интерактивные команды требуют прямой работы с терминалом (например, редакторы).
    Команды с потоковым выводом (ping, tail -f) также запускаются напрямую.

    Args:
        command: Имя команды для проверки

    Returns:
        True если команда требует прямого доступа к терминалу, False иначе
    """
    # Множество команд, которые требуют прямого доступа к терминалу
    interactiveCommands = {
        # Текстовые редакторы
        "nano",
        "vim",
        "vi",
        "emacs",
        "gedit",
        "kate",
        "code",
        # Системные мониторы и утилиты
        "htop",
        "top",
        "less",
        "more",
        "man",
        "watch",
        "btop",
        # Сетевые и удаленные подключения
        "ssh",
        "telnet",
        "ftp",
        "sftp",
        # Многопользовательские терминалы
        "screen",
        "tmux",
        # Файловые менеджеры
        "ranger",
        "mc",
        "ncdu",
        "nnn",
        # Диалоговые утилиты
        "dialog",
        "whiptail",
        "fzf",
        # Отладчики и интерпретаторы
        "gdb",
        "python",
        "python3",
        "ipython",
        "node",
        "nodejs",
        # Базы данных (интерактивные клиенты)
        "mysql",
        "psql",
        "sqlite3",
        "mongo",
        # Ruby интерпретаторы
        "irb",
        "pry",
        # Команды с потоковым выводом (могут работать бесконечно)
        "ping",
        "tail",
        "journalctl",
        "dmesg",
        "tcpdump",
        # Другие shell или командные провайдеры
        "bash",
        "zsh",
    }

    # Проверяем, есть ли команда в списке (без учета регистра)
    return command.lower() in interactiveCommands


def isStreamingCommand(command: str, args: List[str]) -> bool:
    """
    Проверяет, является ли команда потоковой (выводит данные в реальном времени).

    Некоторые команды могут работать бесконечно или выводить данные потоком.
    Такие команды нужно запускать без захвата вывода.

    Args:
        command: Имя команды
        args: Аргументы команды

    Returns:
        True если команда потоковая, False иначе
    """
    # Команды, которые обычно работают с потоковым выводом
    streamingCommands = {
        "ping",  # Работает бесконечно без -c
        "tail",  # С флагом -f работает бесконечно
        "watch",  # Периодически обновляет вывод
        "journalctl",  # Может работать с -f
        "dmesg",  # Может работать с -w
        "tcpdump",  # Перехватывает пакеты в реальном времени
    }

    # Проверяем имя команды
    if command.lower() in streamingCommands:
        return True

    # Для tail проверяем наличие флага -f (follow)
    if command.lower() == "tail" and "-f" in args:
        return True

    # Для journalctl проверяем наличие флага -f (follow)
    if command.lower() == "journalctl" and "-f" in args:
        return True

    return False


def executeExternalCommand(
    command: str, args: List[str], current_directory: str
) -> List[str]:
    """
    Выполняет внешнюю команду системы с правильной обработкой вывода.

    Для интерактивных и потоковых команд запускает их напрямую в терминале.
    Для обычных команд захватывает вывод и возвращает результат.

    Args:
        command: Имя команды для выполнения
        args: Список аргументов команды

    Returns:
        Список из двух элементов: [статус, вывод]
        статус может быть "success" или "error"
    """
    # Проверяем наличие команды в системном PATH
    commandPath = shutil.which(command)

    # Если команда не найдена, возвращаем ошибку
    if not commandPath:
        return ["error", f"Команда '{command}' не найдена в системном PATH"]

    # Определяем, нужно ли запускать команду напрямую в терминале
    needsDirectTerminal = isInteractiveCommand(command) or isStreamingCommand(
        command, args
    )

    # Если команда требует прямого доступа к терминалу
    if needsDirectTerminal:
        try:
            # Запускаем команду без захвата вывода
            # Это позволяет команде работать напрямую с терминалом пользователя
            result = subprocess.run(
                [command] + args,
                cwd=current_directory,  # Передаем текущюю дирикторию DShell
                # Не используем capture_output - команда работает напрямую с терминалом
            )

            # После завершения команды проверяем код возврата
            if result.returncode == 0:
                # Команда завершилась успешно
                return ["success", ""]
            else:
                # Команда завершилась с ошибкой
                return ["error", f"Команда завершилась ошибкой: {result.returncode}"]

        except KeyboardInterrupt:
            # Пользователь прервал выполнение команды (Ctrl+C)
            return ["error", "Пользователь прервал выполнение комнды или программы"]
        except Exception as e:
            # Произошла неожиданная ошибка при выполнении
            return ["error", f"Непредвиденная ошибка при выполнении: {str(e)}"]

    # Для обычных команд захватываем вывод
    try:
        # Запускаем команду с захватом вывода
        result = subprocess.run(
            [command] + args,
            capture_output=True,  # Захватываем stdout и stderr
            text=True,  # Работаем с текстом, а не байтами
            timeout=30,  # Таймаут 30 секунд для предотвращения зависаний
            cwd=current_directory,  # Передаем текущюю дирикторию DShell
        )

        # Объединяем стандартный вывод и вывод ошибок
        output = result.stdout
        if result.stderr:
            # Если есть ошибки, добавляем их к выводу
            output += result.stderr

        # Проверяем код возврата команды
        if result.returncode != 0:
            # Команда завершилась с ошибкой
            return [
                "error",
                f"Команда завершилась с ошибкой:{result.returncode}\n{output}",
            ]

        # Команда выполнена успешно, возвращаем вывод
        return ["success", output.strip() if output else ""]

    except subprocess.TimeoutExpired:
        # Команда превысила лимит времени выполнения
        return [
            "error",
            f"Команда '{command}' превысила лимит времени  выполнении в 30 секунд",
        ]
    except Exception as e:
        # Произошла ошибка при выполнении команды
        return ["error", f"Ошибка выполнения: {str(e)}"]


def isBuiltinCommand(command: str) -> bool:
    """
    Проверяет, является ли команда встроенной в shell.

    Встроенные команды обрабатываются самим shell и не требуют
    выполнения внешних программ.

    Args:
        command: Имя команды для проверки

    Returns:
        True если команда встроенная, False иначе
    """
    # Множество встроенных команд shell
    builtinCommands = {
        # Команды для директорий
        "ls",
        "dir",
        "cd",
        "pwd",
        "mkdir",
        "rmdir",
        # Команды для файлов
        "cat",
        "touch",
        "rm",
        "cp",
        "mv",
        # Команды для поиска
        "grep",
        "find",
        "head",
        "tail",
        "wc",
        # Служебные команды
        "clear",
        "cls",
        "echo",
        "help",
        "history",
        "exit_de",
    }

    # Проверяем, есть ли команда в списке встроенных (без учета регистра)
    return command.lower() in builtinCommands
