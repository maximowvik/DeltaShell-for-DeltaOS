import os
import pwd
import readline
import sys
import traceback
from operator import is_
from textwrap import dedent

from commands import *
from components import *
from parser import *


class Main:
    @staticmethod
    def _setup_readline():
        """Настройка readline для работы со стрелками."""
        if sys.platform != "win32":
            # Настройка для Linux/Unix
            readline.parse_and_bind("tab: complete")
            # Явные привязки для стрелок для GNU readline (Linux)
            # Эти команды обеспечивают работу стрелок влево/вправо и вверх/вниз
            readline.parse_and_bind("\\e[A: history-search-backward")  # Стрелка вверх
            readline.parse_and_bind("\\e[B: history-search-forward")  # Стрелка вниз
            readline.parse_and_bind("\\e[C: forward-char")  # Стрелка вправо
            readline.parse_and_bind("\\e[D: backward-char")  # Стрелка влево
            # Альтернативные escape-последовательности (на случай если первые не работают)
            readline.parse_and_bind("\\eOA: history-search-backward")
            readline.parse_and_bind("\\eOB: history-search-forward")
            readline.parse_and_bind("\\eOC: forward-char")
            readline.parse_and_bind("\\eOD: backward-char")
            readline.set_history_length(1000)

    @staticmethod
    def run():
        input_cmd: str = ""
        current_user: str = f"{pwd.getpwuid(os.getuid()).pw_name}"
        current_host: str = os.uname().nodename
        current_directory: str = (
            f"/home/{current_user}" if is_root() is not True else f"/"
        )

        dir_utility = DirectoryUtility(current_directory)
        history = CommandHistory()

        # Настройка readline для навигации стрелками
        Main._setup_readline()

        message_hello = (
            ConsoleOutput.colorize(
                dedent(f"""
            .____  ____  _          _ _
            |  _ \\/ ___|| |__   ___| | |
            | | | \\___ \\| '_ \\ / _ \\ | |
            | |_| |___) | | | |  __/ | |
            |____/|____/|_|_|_|\\___|_|_|_         ___  ____
            | |__  _   _  |  _ \\  ___| | |_ __ _ / _ \\/ ___|
            | '_ \\| | | | | | | |/ _ \\ | __/ _` | | | \\___ \\
            | |_) | |_| | | |_| |  __/ | || (_| | |_| |___) |
            |_.__/ \\__, | |____/ \\___|_|\\__\\__,_|\\___/|____/
                    |___/
            D S H E L L    by    D e l t a O S
            Author: maximovik
            OS: DeltaOS v0.0.2-1
            """).strip(),
                "cyan",
            )
            + "\n\n"  # Разделяем блоки пустой строкой
            + ConsoleOutput.colorize(
                dedent(f"""
            Добро пожаловать, {current_user}, в Delta Shell!
            Вводя команды, вы можете управлять файловой системой и выполнять различные задачи.
            Введите "help" для получения списка доступных команд.
            """).strip(),
                "white",
            )
            + "\n\n"
            + ConsoleOutput.colorize(
                dedent(
                    "Будьте осторожны при вводе команд и файлов, чтобы избежать ошибок и потери данных."
                ).strip(),
                "red",
            )
        )

        ConsoleOutput.output("info", message_hello)

        while True:
            try:
                # ОБНОВЛЯЕМ текущую директорию каждый раз
                current_directory = dir_utility.get_current_directory()
                prompt = f"[{current_user}@{current_host}][{current_directory}]> "

                # input() автоматически использует readline на Linux, если он настроен
                input_cmd = input(prompt)

                if input_cmd.strip():
                    history.add(input_cmd)
                    # Добавляем в readline для навигации стрелками (избегаем дубликатов)
                    try:
                        hist_len = readline.get_current_history_length()
                        if (
                            hist_len == 0
                            or readline.get_history_item(hist_len) != input_cmd
                        ):
                            readline.add_history(input_cmd)
                    except (OSError, IndexError):
                        readline.add_history(input_cmd)

                if input_cmd.lower() == "exit_de":
                    ConsoleOutput.output("info", "Среда DShell закрыт", "shell")
                    break
                elif not input_cmd.strip():  # Пустая команда
                    continue
                else:
                    tokens = ShellParser.tokenize(input_cmd)
                    result = Command_Base.execute(
                        tokens, dir_utility, history, current_directory
                    )
                    ConsoleOutput.output(result[0], result[1], "shell")

            except KeyboardInterrupt:
                ConsoleOutput.output("info", "\nСреда DShell закрыт (Ctrl+C)", "shell")
                break
            except Exception as e:
                ConsoleOutput.output(
                    "error", f"Error: {e}\n{traceback.format_exc()}", "shell"
                )


def is_root():
    return os.geteuid() == 0


if __name__ == "__main__":
    Main.run()
