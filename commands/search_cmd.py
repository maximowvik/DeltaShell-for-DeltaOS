"""
Команды для поиска и фильтрации данных.
Эти команды помогают находить файлы, искать текст и просматривать части файлов.
"""

import os
import re
from typing import List, Optional

from components import DirectoryUtility


def grepCommand(dirUtility: Optional[DirectoryUtility] = None, args: Optional[List[str]] = None) -> List[str]:
    """
    Ищет текст в файлах.
    
    Использование: grep <текст> <файл>
    Пример: grep "hello" file.txt
    
    Args:
        dirUtility: Утилита для работы с директориями
        args: Список аргументов (текст для поиска, имя файла)
        
    Returns:
        [статус, найденные_строки] или [ошибка, сообщение]
    """
    if dirUtility is None:
        return ["error", "Утилита директорий не предоставлена"]
    
    args = args or []
    
    if len(args) < 2:
        return ["error", "Укажите текст для поиска и файл. Пример: grep \"hello\" file.txt"]
    
    searchText = args[0]
    filename = args[1]
    
    currentDir = dirUtility.get_current_directory()
    filePath = os.path.join(currentDir, filename)
    
    if os.path.isabs(filename):
        filePath = filename
    
    if not os.path.exists(filePath) or not os.path.isfile(filePath):
        return ["error", f"Файл не найден: {filePath}"]
    
    try:
        matches = []
        with open(filePath, 'r', encoding='utf-8', errors='ignore') as f:
            for lineNum, line in enumerate(f, 1):
                if searchText in line:
                    matches.append(f"{lineNum}: {line.rstrip()}")
        
        if matches:
            return ["success", "\n".join(matches)]
        else:
            return ["success", f"Текст '{searchText}' не найден в файле"]
    except Exception as e:
        return ["error", f"Ошибка при поиске: {str(e)}"]


def findCommand(dirUtility: Optional[DirectoryUtility] = None, args: Optional[List[str]] = None) -> List[str]:
    """
    Находит файлы и директории по имени.
    
    Использование: find <имя> или find . -name <имя>
    Пример: find "*.txt"
    Пример: find . -name "test*"
    
    Args:
        dirUtility: Утилита для работы с директориями
        args: Список аргументов
        
    Returns:
        [статус, найденные_файлы] или [ошибка, сообщение]
    """
    if dirUtility is None:
        return ["error", "Утилита директорий не предоставлена"]
    
    args = args or []
    
    if not args:
        return ["error", "Укажите имя для поиска. Пример: find \"*.txt\""]
    
    # Упрощенная версия find - ищем по шаблону в текущей директории
    searchPattern = args[-1]  # Последний аргумент - это шаблон
    
    # Убираем кавычки если есть
    searchPattern = searchPattern.strip('"\'')
    
    # Преобразуем простой шаблон в регулярное выражение
    pattern = searchPattern.replace('*', '.*').replace('?', '.')
    
    currentDir = dirUtility.get_current_directory()
    found = []
    
    try:
        for root, dirs, files in os.walk(currentDir):
            # Ищем в файлах
            for name in files:
                if re.match(pattern, name, re.IGNORECASE):
                    fullPath = os.path.join(root, name)
                    found.append(fullPath)
            
            # Ищем в директориях
            for name in dirs:
                if re.match(pattern, name, re.IGNORECASE):
                    fullPath = os.path.join(root, name)
                    found.append(fullPath)
        
        if found:
            return ["success", "\n".join(found[:100])]  # Ограничиваем 100 результатами
        else:
            return ["success", f"Ничего не найдено по шаблону: {searchPattern}"]
    except Exception as e:
        return ["error", f"Ошибка при поиске: {str(e)}"]


def headCommand(dirUtility: Optional[DirectoryUtility] = None, args: Optional[List[str]] = None) -> List[str]:
    """
    Показывает первые строки файла.
    
    Использование: head <файл> или head -n 10 <файл>
    Пример: head file.txt
    Пример: head -n 5 file.txt
    
    Args:
        dirUtility: Утилита для работы с директориями
        args: Список аргументов
        
    Returns:
        [статус, строки] или [ошибка, сообщение]
    """
    if dirUtility is None:
        return ["error", "Утилита директорий не предоставлена"]
    
    args = args or []
    
    if not args:
        return ["error", "Укажите имя файла. Пример: head file.txt"]
    
    # По умолчанию показываем 10 строк
    numLines = 10
    filename = args[-1]
    
    # Проверяем флаг -n
    if "-n" in args:
        try:
            nIndex = args.index("-n")
            if nIndex + 1 < len(args):
                numLines = int(args[nIndex + 1])
        except (ValueError, IndexError):
            pass
    
    currentDir = dirUtility.get_current_directory()
    filePath = os.path.join(currentDir, filename)
    
    if os.path.isabs(filename):
        filePath = filename
    
    if not os.path.exists(filePath) or not os.path.isfile(filePath):
        return ["error", f"Файл не найден: {filePath}"]
    
    try:
        with open(filePath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = []
            for i, line in enumerate(f):
                if i >= numLines:
                    break
                lines.append(line.rstrip())
        
        return ["success", "\n".join(lines)]
    except Exception as e:
        return ["error", f"Ошибка при чтении файла: {str(e)}"]


def tailCommand(dirUtility: Optional[DirectoryUtility] = None, args: Optional[List[str]] = None) -> List[str]:
    """
    Показывает последние строки файла.
    
    Использование: tail <файл> или tail -n 10 <файл>
    Пример: tail file.txt
    Пример: tail -n 5 file.txt
    
    Args:
        dirUtility: Утилита для работы с директориями
        args: Список аргументов
        
    Returns:
        [статус, строки] или [ошибка, сообщение]
    """
    if dirUtility is None:
        return ["error", "Утилита директорий не предоставлена"]
    
    args = args or []
    
    if not args:
        return ["error", "Укажите имя файла. Пример: tail file.txt"]
    
    # По умолчанию показываем 10 строк
    numLines = 10
    filename = args[-1]
    
    # Проверяем флаг -n
    if "-n" in args:
        try:
            nIndex = args.index("-n")
            if nIndex + 1 < len(args):
                numLines = int(args[nIndex + 1])
        except (ValueError, IndexError):
            pass
    
    currentDir = dirUtility.get_current_directory()
    filePath = os.path.join(currentDir, filename)
    
    if os.path.isabs(filename):
        filePath = filename
    
    if not os.path.exists(filePath) or not os.path.isfile(filePath):
        return ["error", f"Файл не найден: {filePath}"]
    
    try:
        with open(filePath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            # Берем последние numLines строк
            lastLines = lines[-numLines:] if len(lines) > numLines else lines
            result = [line.rstrip() for line in lastLines]
        
        return ["success", "\n".join(result)]
    except Exception as e:
        return ["error", f"Ошибка при чтении файла: {str(e)}"]


def wcCommand(dirUtility: Optional[DirectoryUtility] = None, args: Optional[List[str]] = None) -> List[str]:
    """
    Подсчитывает количество строк, слов и символов в файле.
    
    Использование: wc <файл>
    Пример: wc file.txt
    
    Args:
        dirUtility: Утилита для работы с директориями
        args: Список аргументов
        
    Returns:
        [статус, статистика] или [ошибка, сообщение]
    """
    if dirUtility is None:
        return ["error", "Утилита директорий не предоставлена"]
    
    args = args or []
    
    if not args:
        return ["error", "Укажите имя файла. Пример: wc file.txt"]
    
    filename = args[0]
    currentDir = dirUtility.get_current_directory()
    filePath = os.path.join(currentDir, filename)
    
    if os.path.isabs(filename):
        filePath = filename
    
    if not os.path.exists(filePath) or not os.path.isfile(filePath):
        return ["error", f"Файл не найден: {filePath}"]
    
    try:
        with open(filePath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.count('\n')
            words = len(content.split())
            chars = len(content)
        
        result = f"Строк: {lines}, Слов: {words}, Символов: {chars} - {filePath}"
        return ["success", result]
    except Exception as e:
        return ["error", f"Ошибка при чтении файла: {str(e)}"]

