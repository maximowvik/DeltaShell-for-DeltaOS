from typing import List, Optional


class CommandHistory:
    """Временная история команд только для текущей сессии."""

    def __init__(self, max_entries: int = 1000):
        self.max_entries = max_entries
        self._entries: List[str] = []

    def add(self, command: str):
        """Добавляет команду в историю."""
        command = (command or "").strip()
        if not command:
            return

        # Не добавляем дубликаты подряд
        if self._entries and self._entries[-1] == command:
            return

        self._entries.append(command)
        if len(self._entries) > self.max_entries:
            self._entries = self._entries[-self.max_entries :]

    def format(self, limit: Optional[int] = None) -> str:
        """Форматирует историю для вывода."""
        if not self._entries:
            return "History is empty"

        entries = self._entries if limit is None else self._entries[-limit:]
        start_index = len(self._entries) - len(entries) + 1
        lines = [f"{idx}. {cmd}" for idx, cmd in enumerate(entries, start=start_index)]
        return "\n".join(lines)

    def clear(self):
        """Очищает историю."""
        self._entries.clear()

    def get_all(self) -> List[str]:
        """Возвращает все записи истории."""
        return self._entries.copy()

