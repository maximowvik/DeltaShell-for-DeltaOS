"""
Команды для работы с файлами.
Эти команды позволяют создавать, читать, копировать, перемещать и удалять файлы.
"""

import os
import shutil
from typing import List, Optional

from components import DirectoryUtility


def catCommand(dirUtility: Optional[DirectoryUtility] = None, args: Optional[List[str]] = None) -> List[str]:
    """
    Показывает содержимое файла.
    
    Использование: cat <имя_файла>
    Пример: cat readme.txt
    
    Args:
        dirUtility: Утилита для работы с директориями
        args: Список аргументов (имя файла)
        
    Returns:
        [статус, содержимое_файла] или [ошибка, сообщение]
    """
    if dirUtility is None:
        return ["error", "Утилита директорий не предоставлена"]
    
    args = args or []
    
    # Проверяем, что указан файл
    if not args:
        return ["error", "Укажите имя файла. Пример: cat readme.txt"]
    
    # Получаем путь к файлу
    filename = args[0]
    currentDir = dirUtility.get_current_directory()
    filePath = os.path.join(currentDir, filename)
    
    # Если путь абсолютный, используем его
    if os.path.isabs(filename):
        filePath = filename
    
    # Проверяем, существует ли файл
    if not os.path.exists(filePath):
        return ["error", f"Файл не найден: {filePath}"]
    
    # Проверяем, что это файл, а не директория
    if not os.path.isfile(filePath):
        return ["error", f"Это не файл: {filePath}"]
    
    try:
        # Читаем и возвращаем содержимое файла
        with open(filePath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        return ["success", content]
    except Exception as e:
        return ["error", f"Ошибка при чтении файла: {str(e)}"]


def touchCommand(dirUtility: Optional[DirectoryUtility] = None, args: Optional[List[str]] = None) -> List[str]:
    """
    Создает новый пустой файл или обновляет время изменения существующего.
    
    Использование: touch <имя_файла>
    Пример: touch newfile.txt
    
    Args:
        dirUtility: Утилита для работы с директориями
        args: Список аргументов (имя файла)
        
    Returns:
        [статус, сообщение]
    """
    if dirUtility is None:
        return ["error", "Утилита директорий не предоставлена"]
    
    args = args or []
    
    if not args:
        return ["error", "Укажите имя файла. Пример: touch newfile.txt"]
    
    filename = args[0]
    currentDir = dirUtility.get_current_directory()
    filePath = os.path.join(currentDir, filename)
    
    if os.path.isabs(filename):
        filePath = filename
    
    try:
        # Создаем пустой файл или обновляем время изменения
        with open(filePath, 'a'):
            os.utime(filePath, None)
        
        if os.path.exists(filePath):
            return ["success", f"Файл создан или обновлен: {filePath}"]
        else:
            return ["success", f"Файл создан: {filePath}"]
    except Exception as e:
        return ["error", f"Ошибка при создании файла: {str(e)}"]


def rmCommand(dirUtility: Optional[DirectoryUtility] = None, args: Optional[List[str]] = None) -> List[str]:
    """
    Удаляет файл или директорию.
    
    Использование: rm <имя_файла> или rm -r <директория>
    Пример: rm oldfile.txt
    Пример: rm -r olddir
    
    Args:
        dirUtility: Утилита для работы с директориями
        args: Список аргументов
        
    Returns:
        [статус, сообщение]
    """
    if dirUtility is None:
        return ["error", "Утилита директорий не предоставлена"]
    
    args = args or []
    
    if not args:
        return ["error", "Укажите имя файла или директории. Пример: rm file.txt"]
    
    # Проверяем флаг -r для рекурсивного удаления
    recursive = "-r" in args or "-R" in args or "--recursive" in args
    
    # Получаем имя файла/директории (последний аргумент, не флаг)
    target = None
    for arg in reversed(args):
        if arg not in ["-r", "-R", "--recursive"]:
            target = arg
            break
    
    if not target:
        return ["error", "Укажите имя файла или директории"]
    
    currentDir = dirUtility.get_current_directory()
    targetPath = os.path.join(currentDir, target)
    
    if os.path.isabs(target):
        targetPath = target
    
    if not os.path.exists(targetPath):
        return ["error", f"Файл или директория не найдены: {targetPath}"]
    
    try:
        if os.path.isdir(targetPath):
            # Удаляем директорию
            if recursive:
                shutil.rmtree(targetPath)
                return ["success", f"Директория удалена: {targetPath}"]
            else:
                return ["error", f"Для удаления директории используйте флаг -r: rm -r {target}"]
        else:
            # Удаляем файл
            os.remove(targetPath)
            return ["success", f"Файл удален: {targetPath}"]
    except Exception as e:
        return ["error", f"Ошибка при удалении: {str(e)}"]


def cpCommand(dirUtility: Optional[DirectoryUtility] = None, args: Optional[List[str]] = None) -> List[str]:
    """
    Копирует файл или директорию.
    
    Использование: cp <источник> <назначение>
    Пример: cp file.txt backup.txt
    Пример: cp -r dir1 dir2
    
    Args:
        dirUtility: Утилита для работы с директориями
        args: Список аргументов
        
    Returns:
        [статус, сообщение]
    """
    if dirUtility is None:
        return ["error", "Утилита директорий не предоставлена"]
    
    args = args or []
    
    if len(args) < 2:
        return ["error", "Укажите источник и назначение. Пример: cp file.txt backup.txt"]
    
    # Проверяем флаг -r для рекурсивного копирования
    recursive = "-r" in args or "-R" in args or "--recursive" in args
    
    # Получаем источник и назначение (исключая флаги)
    source = None
    destination = None
    
    for arg in args:
        if arg not in ["-r", "-R", "--recursive"]:
            if source is None:
                source = arg
            elif destination is None:
                destination = arg
                break
    
    if not source or not destination:
        return ["error", "Укажите источник и назначение. Пример: cp file.txt backup.txt"]
    
    currentDir = dirUtility.get_current_directory()
    sourcePath = os.path.join(currentDir, source) if not os.path.isabs(source) else source
    destPath = os.path.join(currentDir, destination) if not os.path.isabs(destination) else destination
    
    if not os.path.exists(sourcePath):
        return ["error", f"Источник не найден: {sourcePath}"]
    
    try:
        if os.path.isdir(sourcePath):
            # Копируем директорию
            if recursive:
                shutil.copytree(sourcePath, destPath, dirs_exist_ok=True)
                return ["success", f"Директория скопирована: {sourcePath} -> {destPath}"]
            else:
                return ["error", f"Для копирования директории используйте флаг -r: cp -r {source} {destination}"]
        else:
            # Копируем файл
            shutil.copy2(sourcePath, destPath)
            return ["success", f"Файл скопирован: {sourcePath} -> {destPath}"]
    except Exception as e:
        return ["error", f"Ошибка при копировании: {str(e)}"]


def mvCommand(dirUtility: Optional[DirectoryUtility] = None, args: Optional[List[str]] = None) -> List[str]:
    """
    Перемещает или переименовывает файл или директорию.
    
    Использование: mv <источник> <назначение>
    Пример: mv oldname.txt newname.txt
    Пример: mv file.txt /home/user/
    
    Args:
        dirUtility: Утилита для работы с директориями
        args: Список аргументов
        
    Returns:
        [статус, сообщение]
    """
    if dirUtility is None:
        return ["error", "Утилита директорий не предоставлена"]
    
    args = args or []
    
    if len(args) < 2:
        return ["error", "Укажите источник и назначение. Пример: mv old.txt new.txt"]
    
    source = args[0]
    destination = args[1]
    
    currentDir = dirUtility.get_current_directory()
    sourcePath = os.path.join(currentDir, source) if not os.path.isabs(source) else source
    destPath = os.path.join(currentDir, destination) if not os.path.isabs(destination) else destination
    
    if not os.path.exists(sourcePath):
        return ["error", f"Источник не найден: {sourcePath}"]
    
    try:
        # Перемещаем файл или директорию
        shutil.move(sourcePath, destPath)
        return ["success", f"Перемещено: {sourcePath} -> {destPath}"]
    except Exception as e:
        return ["error", f"Ошибка при перемещении: {str(e)}"]

