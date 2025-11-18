"""
Команда help - показывает справку по командам.
Поддерживает общую справку и справку по конкретной команде.
"""

import os
import shutil
import subprocess
from textwrap import dedent
from typing import Dict, Optional

from components.console_output import ConsoleOutput

# Описания встроенных команд
BUILTIN_COMMAND_DESCRIPTIONS: Dict[str, str] = {
    # Команды для директорий
    "ls": "Показать содержимое директории. Используйте -a для скрытых файлов, -l для подробной информации.",
    "dir": "Альтернативное имя для команды ls.",
    "cd": "Перейти в указанную директорию. Используйте .. для перехода на уровень выше.",
    "pwd": "Показать полный путь к текущей директории.",
    "mkdir": "Создать новую директорию по указанному пути.",
    "rmdir": "Удалить пустую директорию.",
    # Команды для файлов
    "cat": "Показать содержимое файла целиком.",
    "touch": "Создать новый пустой файл или обновить время изменения существующего.",
    "rm": "Удалить файл или директорию. Используйте -r для удаления директорий с содержимым.",
    "cp": "Скопировать файл или директорию. Используйте -r для копирования директорий.",
    "mv": "Переместить или переименовать файл или директорию.",
    # Команды для поиска
    "grep": "Найти и показать строки, содержащие указанный текст в файле.",
    "find": "Найти файлы и директории по шаблону имени (поддерживает * и ?).",
    "head": "Показать первые строки файла. Используйте -n для указания количества строк.",
    "tail": "Показать последние строки файла. Используйте -n для указания количества строк.",
    "wc": "Подсчитать количество строк, слов и символов в файле.",
    # Служебные команды
    "echo": "Вывести указанный текст на экран.",
    "history": "Показать историю введенных команд. Можно указать количество последних команд.",
    "clear": "Очистить экран терминала.",
    "cls": "Альтернативное имя для команды clear.",
    "help": "Показать справку по командам. Используйте help --команда для справки по конкретной команде.",
    "exit_de": "Выйти из Delta Shell.",
}


def getCommandDescriptionFromSystem(command: str) -> Optional[str]:
    """
    Получает описание команды из системы через --help или man.

    Args:
        command: Имя команды

    Returns:
        Описание команды или None, если не удалось получить
    """
    # Проверяем, существует ли команда
    if not shutil.which(command):
        return None

    # Пробуем получить описание через --help
    try:
        result = subprocess.run(
            [command, "--help"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0 and result.stdout:
            # Берем первую строку описания (обычно это краткое описание)
            lines = result.stdout.strip().split("\n")
            for line in lines[:5]:  # Проверяем первые 5 строк
                line = line.strip()
                if (
                    line
                    and not line.startswith("Usage:")
                    and not line.startswith("Options:")
                ):
                    # Убираем лишние пробелы и возвращаем краткое описание
                    if len(line) > 200:
                        line = line[:200] + "..."
                    return line
    except (subprocess.TimeoutExpired, Exception):
        pass

    # Если --help не сработал, пробуем man (только первую строку)
    try:
        result = subprocess.run(
            ["man", "-f", command],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0 and result.stdout:
            # man -f возвращает краткое описание
            description = result.stdout.strip().split("\n")[0]
            # Убираем имя команды и оставляем только описание
            parts = description.split(" - ", 1)
            if len(parts) > 1:
                return parts[1]
            return description
    except (subprocess.TimeoutExpired, Exception):
        pass

    return None


def formatHelpTable() -> str:
    """
    Форматирует общую справку в виде красивой таблицы без лишних пустых строк.
    """
    width = os.get_terminal_size().columns

    # Цвета
    border_color = ConsoleOutput.COLORS["cyan"]
    title_color = ConsoleOutput.COLORS["bright_cyan"] + ConsoleOutput.COLORS["bold"]
    category_color = (
        ConsoleOutput.COLORS["bright_yellow"] + ConsoleOutput.COLORS["bold"]
    )
    command_color = ConsoleOutput.COLORS["bright_green"]
    desc_color = ConsoleOutput.COLORS["white"]
    hint_color = ConsoleOutput.COLORS["bright_blue"]
    reset = ConsoleOutput.COLORS["reset"]

    lines = []

    # Верхняя граница
    lines.append(f"{border_color}╔{'═' * (width - 2)}╗{reset}")

    # Заголовок
    title = "DELTA SHELL - СПРАВКА ПО КОМАНДАМ"
    pad_left = (width - len(title) - 2) // 2
    pad_right = width - len(title) - 2 - pad_left
    title_line = f"{border_color}║{reset}{pad_left * ' '}{title_color}{title}{reset}{pad_right * ' '}{border_color}║{reset}"
    lines.append(title_line)

    # Разделитель после заголовка
    lines.append(f"{border_color}╠{'═' * (width - 2)}╣{reset}")

    categories = {
        "  📁 Директории": [
            ("ls, dir", "Показать содержимое директории"),
            ("cd <путь>", "Перейти в директорию"),
            ("pwd", "Текущая директория"),
            ("mkdir <путь>", "Создать директорию"),
            ("rmdir <путь>", "Удалить директорию"),
        ],
        "  📄 Файлы": [
            ("cat <файл>", "Показать содержимое файла"),
            ("touch <файл>", "Создать файл"),
            ("rm <файл>", "Удалить файл (-r для директорий)"),
            ("cp <от> <куда>", "Копировать (-r для директорий)"),
            ("mv <от> <куда>", "Переместить/переименовать"),
        ],
        "  🔍 Поиск": [
            ("grep <текст> <файл>", "Найти текст в файле"),
            ("find <шаблон>", "Найти файлы по имени"),
            ("head <файл>", "Первые строки (-n для количества)"),
            ("tail <файл>", "Последние строки (-n для количества)"),
            ("wc <файл>", "Подсчет строк, слов, символов"),
        ],
        "  🔍 Служебные": [
            ("echo <текст>", "Вывести текст"),
            ("history [N]", "История команд"),
            ("clear, cls", "Очистить экран"),
            ("help [--команда]", "Справка (help --команда для деталей)"),
            ("exit_de", "Выйти из shell"),
        ],
    }

    for category, commands in categories.items():
        # Название категории
        lines.append(
            f"{border_color}║{reset}{category_color}{category}{reset}{' ' * (width - len(category) - 3)}{border_color}║{reset}"
        )
        lines.append(f"{border_color}╠{'=' * (width - 2)}╣{reset}")

        cmd_width = max(10, int(width * 0.28))
        desc_width = width - cmd_width - 5  # 2 пробела слева и справа

        for cmd, desc in commands:
            cmd_colored = f"{command_color}{cmd}{reset}"
            cmd_padding = " " * (cmd_width - len(cmd))

            words = desc.split()
            current_line = ""
            first = True

            for word in words:
                test = current_line + word + " "
                if len(test) > desc_width and current_line:
                    desc_line = f"{desc_color}{current_line.strip()}{reset}"
                    desc_pad = " " * (desc_width - len(current_line.strip()))
                    if first:
                        lines.append(
                            f"{border_color}║{reset}  {cmd_colored}{cmd_padding} {desc_line}{desc_pad}{border_color}║{reset}"
                        )
                        first = False
                    else:
                        lines.append(
                            f"{border_color}║{reset}{' ' * (cmd_width + 2)} {desc_line}{desc_pad}{border_color}║{reset}"
                        )
                    current_line = word + " "
                else:
                    current_line = test

            if current_line.strip():
                desc_line = f"{desc_color}{current_line.strip()}{reset}"
                desc_pad = " " * (desc_width - len(current_line.strip()))
                if first:
                    lines.append(
                        f"{border_color}║{reset}  {cmd_colored}{cmd_padding} {desc_line}{desc_pad}{border_color}║{reset}"
                    )
                else:
                    lines.append(
                        f"{border_color}║{reset}{' ' * (cmd_width + 2)} {desc_line}{desc_pad}{border_color}║{reset}"
                    )

        # Разделитель между категориями
        lines.append(f"{border_color}╠{'─' * (width - 2)}╣{reset}")

    # Подсказки
    hint1 = "💡 ПОДСКАЗКА: Используйте 'help --команда' для подробной справки"
    hint2 = "   Вы также можете использовать любые команды Linux из системы!"

    if len(hint1) <= width - 2:
        lines.append(
            f"{border_color}║{reset} {hint_color}{hint1}{reset}{' ' * (width - len(hint1) - 4)}{border_color}║{reset}"
        )
    else:
        lines.append(
            f"{border_color}║{reset} {hint_color}{hint1[: width - 5]}...{reset} {border_color}║{reset}"
        )

    if len(hint2) <= width - 2:
        lines.append(
            f"{border_color}║{reset} {hint_color}{hint2}{reset}{' ' * (width - len(hint2) - 3)}{border_color}║{reset}"
        )
    else:
        lines.append(
            f"{border_color}║{reset} {hint_color}{hint2[: width - 5]}...{reset} {border_color}║{reset}"
        )

    # Нижняя граница
    lines.append(f"{border_color}╚{'═' * (width - 2)}╝{reset}")

    return "\n".join(lines)


def getCommandHelp(commandName: str) -> str:
    """
    Возвращает справку по конкретной команде с адаптивной шириной.
    """
    width = os.get_terminal_size().columns
    commandName = commandName.lower()

    border_color = ConsoleOutput.COLORS["cyan"]
    title_color = ConsoleOutput.COLORS["bright_cyan"] + ConsoleOutput.COLORS["bold"]
    command_color = ConsoleOutput.COLORS["bright_green"] + ConsoleOutput.COLORS["bold"]
    desc_color = ConsoleOutput.COLORS["white"]
    example_color = ConsoleOutput.COLORS["bright_yellow"]
    error_color = ConsoleOutput.COLORS["bright_red"]
    reset = ConsoleOutput.COLORS["reset"]

    examples = {
        "ls": dedent("""
            ls -a                   # Показать все файлы включая скрытые
            ls -l                   # Подробная информация
            """).strip(),
        "cd": dedent("""
            cd /home/user           # Перейти в директорию
            cd ..                   # На уровень выше
            """).strip(),
        "cat": dedent("""
            cat file.txt            # Показать содержимое файла
            """).strip(),
        "grep": dedent("""
            grep "hello" file.txt   # Найти слово 'hello' в файле
            """).strip(),
        "find": dedent("""
            find "*.txt"            # Найти все .txt файлы
            """).strip(),
        "head": dedent("""
            head file.txt           # Первые 10 строк
            head -n 5 file.txt      # Первые 5 строк
            """).strip(),
        "tail": dedent("""
            tail file.txt           # Последние 10 строк
            tail -n 5 file.txt      # Последние 5 строк
            """).strip(),
        "cp": dedent("""
            cp file.txt backup.txt  # Копировать файл
            cp -r dir1 dir2         # Копировать директорию
            """).strip(),
        "mv": dedent("""
            mv old.txt new.txt      # Переименовать
            mv file.txt /tmp/       # Переместить
            """).strip(),
        "rm": dedent("""
            rm file.txt             # Удалить файл
            rm -r directory         # Удалить директорию
            """).strip(),
    }

    lines = []
    lines.append(f"{border_color}╔{'═' * (width - 2)}╗{reset}")

    full_title_text = f"КОМАНДА: {commandName.upper()}"
    padding = " " * (width - len(full_title_text) - 3)
    title_line = f"{border_color}║{reset} {title_color}{full_title_text}{reset}{padding}{border_color}║{reset}"
    lines.append(title_line)
    lines.append(f"{border_color}╠{'═' * (width - 2)}╣{reset}")

    content_lines = []

    if commandName in BUILTIN_COMMAND_DESCRIPTIONS:
        description = BUILTIN_COMMAND_DESCRIPTIONS[commandName]
        content_lines.append(description)
        has_examples = commandName in examples
    else:
        system_desc = getCommandDescriptionFromSystem(commandName)
        if system_desc:
            content_lines.append(system_desc)
            has_examples = False
        else:
            content_lines = [
                f"Команда '{commandName}' не найдена.",
                "Используйте 'help' для списка доступных команд.",
            ]
            has_examples = False
            # Оставим цвет ошибки ниже

    desc_width = width - 3  # отступы слева и справа

    for i, line in enumerate(content_lines):
        if "не найдена" in line or "списка" in line:
            color = error_color
        else:
            color = desc_color

        words = line.split()
        current = ""
        for word in words:
            test = current + word + " "
            if len(test) > desc_width and current:
                pad = " " * (desc_width - len(current.strip()))
                lines.append(
                    f"{border_color}║{reset} {color}{current.strip()}{reset}{pad}{border_color}║{reset}"
                )
                current = word + " "
            else:
                current = test
        if current.strip():
            pad = " " * (desc_width - len(current.strip()))
            lines.append(
                f"{border_color}║{reset} {color}{current.strip()}{reset}{pad}{border_color}║{reset}"
            )

    if has_examples:
        lines.append(f"{border_color}╠{'─' * (width - 2)}╣{reset}")
        ex_title = "ПРИМЕРЫ ИСПОЛЬЗОВАНИЯ:"
        pad = " " * (width - len(ex_title) - 3)
        lines.append(
            f"{border_color}║{reset} {title_color}{ex_title}{reset}{pad}{border_color}║{reset}"
        )
        for ex_line in examples[commandName].split("\n"):
            pad_ex = " " * (width - len(ex_line) - 5)
            lines.append(
                f"{border_color}║{reset}   {example_color}{ex_line}{reset}{pad_ex}{border_color}║{reset}"
            )

    lines.append(f"{border_color}╚{'═' * (width - 2)}╝{reset}")

    return "\n".join(lines)
