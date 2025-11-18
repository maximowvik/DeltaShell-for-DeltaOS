# commands.py
from optparse import Option
from typing import Callable, Dict, List, Optional, Tuple

from components import CommandHistory, DirectoryUtility

from .clear_cmd import clear_cmd
from .dir_actions_cmd import mkdir_cmd, rmdir_cmd
from .dir_cmd import cd_cmd, ls_cmd, pwd_cmd
from .external_cmd import executeExternalCommand, isBuiltinCommand
from .file_cmd import catCommand, cpCommand, mvCommand, rmCommand, touchCommand
from .help_cmd import formatHelpTable, getCommandHelp
from .search_cmd import findCommand, grepCommand, headCommand, tailCommand, wcCommand

CommandResult = List[str]
CommandHandler = Callable[[Optional[DirectoryUtility], List[str]], CommandResult]

# Возможные операторы перенаправления
REDIRECT_OPERATORS = {">", ">>", "<", "2>", "&>"}


class Command_Base:
    """Простой диспетчер команд оболочки."""

    _command_map: Dict[str, CommandHandler] = {
        # Команды для работы с директориями
        "ls": ls_cmd,
        "dir": ls_cmd,
        "cd": cd_cmd,
        "pwd": pwd_cmd,
        "mkdir": mkdir_cmd,
        "rmdir": rmdir_cmd,
        # Команды для работы с файлами
        "cat": catCommand,
        "touch": touchCommand,
        "rm": rmCommand,
        "cp": cpCommand,
        "mv": mvCommand,
        # Команды для поиска и фильтрации
        "grep": grepCommand,
        "find": findCommand,
        "head": headCommand,
        "tail": tailCommand,
        "wc": wcCommand,
    }

    _clear_aliases = {"clear", "cls"}

    @staticmethod
    def _parse_redirects(
        tokens: List[str],
    ) -> Tuple[List[str], Optional[str], Optional[str], bool]:
        """
        Разбирает токены на команду и инструкции по перенаправлению.

        Args:
            tokens: Список токенов команды, включая перенаправления.

        Returns:
            Кортеж (args_before_redirect, output_file, input_file, append_mode),
            где:
            - args_before_redirect: список аргументов команды до перенаправления
            - output_file: имя файла для вывода или None
            - input_file: имя файла для ввода или None (пока не реализовано)
            - append_mode: True если используется '>>', False если '>'
        """
        args = []
        output_file = None
        input_file = None
        append_mode = False
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if token in REDIRECT_OPERATORS:
                if token == ">":
                    if i + 1 < len(tokens):
                        output_file = tokens[i + 1]
                        append_mode = False
                        i += 2  # Пропускаем оператор и файл
                        continue
                    else:
                        return (
                            ["error", f"Оператор '{token}' требует имя файла"],
                            None,
                            None,
                            False,
                        )
                elif token == ">>":
                    if i + 1 < len(tokens):
                        output_file = tokens[i + 1]
                        append_mode = True
                        i += 2
                        continue
                    else:
                        return (
                            ["error", f"Оператор '{token}' требует имя файла"],
                            None,
                            None,
                            False,
                        )
                elif token == "<":
                    # TODO: Реализовать перенаправление ввода
                    return (
                        [
                            "error",
                            f"Перенаправление ввода '{token}' пока не реализовано",
                        ],
                        None,
                        None,
                        False,
                    )
                elif token == "2>":
                    # TODO: Реализовать перенаправление stderr
                    return (
                        [
                            "error",
                            f"Перенаправление stderr '{token}' пока не реализовано",
                        ],
                        None,
                        None,
                        False,
                    )
                elif token == "&>":
                    # TODO: Реализовать перенаправление stdout и stderr
                    return (
                        [
                            "error",
                            f"Перенаправление stdout и stderr '{token}' пока не реализовано",
                        ],
                        None,
                        None,
                        False,
                    )
                else:
                    # Неожиданный оператор
                    return (
                        ["error", f"Неизвестный оператор перенаправления '{token}'"],
                        None,
                        None,
                        False,
                    )
            else:
                args.append(token)
            i += 1

        return args, output_file, input_file, append_mode

    @staticmethod
    def execute(
        tokens: Optional[List[str]] = None,
        dir_utility: Optional[DirectoryUtility] = None,
        history: Optional[CommandHistory] = None,
        current_directory: str = None,
    ):
        if not tokens:
            return ["error", "Команда не указана"]

        args_before_redirect, output_file, input_file, append_mode = (
            Command_Base._parse_redirects(tokens)
        )

        # Проверяем, вернула ли _parse_redirects ошибку
        if (
            isinstance(args_before_redirect, list)
            and len(args_before_redirect) == 0
            and output_file is None
        ):
            # Это означает, что _parse_redirects вернула ошибку (первый элемент - ["error", ...])
            if (
                isinstance(args_before_redirect[0], str)
                and args_before_redirect[0] == "error"
            ):
                return args_before_redirect  # Возвращаем результат ошибки

        if not args_before_redirect:
            return ["error", "Команда не указана до перенаправления"]

        command, *args = args_before_redirect
        command = command.lower()

        handler = Command_Base._command_map.get(command)
        if handler:
            result = handler(dir_utility, args)
        elif command == "history":
            if history is None:
                return ["error", "История недоступна"]

            limit = None
            if args:
                try:
                    limit = max(1, int(args[0]))
                except ValueError:
                    return ["error", "Лимит истории должен быть числом"]
            result = ["success", history.format(limit)]
        elif command in Command_Base._clear_aliases:
            clear_cmd()
            result = ["success", "Shell очищен"]
        elif command == "echo":
            result = ["success", " ".join(args)]
        elif command == "help":
            if args and len(args) > 0:
                cmdName = args[0]
                if cmdName.startswith("--"):
                    cmdName = cmdName[2:]
                result = ["success", getCommandHelp(cmdName)]
            else:
                result = ["success", formatHelpTable()]
        elif not isBuiltinCommand(command):
            # Передаем current_directory в executeExternalCommand
            result = executeExternalCommand(command, args, current_directory)
        else:  # <-- Вот это else теперь корректно ловит все команды, которые не встроенные и не внешние
            result = [
                "error",
                f"Команда '{command}' не найдена. Введите 'help' для получения доступных команд.",
            ]

        # --- Обработка перенаправления ---
        if output_file:
            try:
                # Разрешаем путь к файлу относительно текущей директории DShell
                resolved_output_path = (
                    dir_utility._resolve_path(output_file)
                    if dir_utility
                    else output_file
                )

                mode = "a" if append_mode else "w"
                with open(resolved_output_path, mode, encoding="utf-8") as f:
                    if result[0] == "success":
                        f.write(result[1])
                        # Если перенаправление, не выводим в терминал успех, только в файл
                        # Возвращаем пустую строку или сообщение об успехе перенаправления
                        return [
                            "success",
                            f"Вывод команды '{command}' перенаправлен в {resolved_output_path}",
                        ]
                    elif result[0] == "error":
                        # Опционально: записывать ошибки в файл или выводить в stderr
                        # Здесь просто записываем ошибку в файл, как и обычный вывод
                        f.write(result[1])
                        return [
                            "error",
                            f"Ошибка команды '{command}', подробности в {resolved_output_path}",
                        ]

            except IOError as e:
                return ["error", f"Ошибка при записи в файл {output_file}: {e}"]
        # --- Конец обработки перенаправления ---

        # Если не было перенаправления, возвращаем результат как есть
        return result  # <-- ВАЖНО: Этот return должен быть всегда
