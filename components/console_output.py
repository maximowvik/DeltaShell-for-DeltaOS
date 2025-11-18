class ConsoleOutput:
    """Класс для красивого вывода сообщений с поддержкой цветов."""
    
    # ANSI коды цветов
    COLORS = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "dim": "\033[2m",
        # Основные цвета
        "black": "\033[30m",
        "red": "\033[31m",
        "green": "\033[32m",
        "yellow": "\033[33m",
        "blue": "\033[34m",
        "magenta": "\033[35m",
        "cyan": "\033[36m",
        "white": "\033[37m",
        # Яркие цвета
        "bright_black": "\033[90m",
        "bright_red": "\033[91m",
        "bright_green": "\033[92m",
        "bright_yellow": "\033[93m",
        "bright_blue": "\033[94m",
        "bright_magenta": "\033[95m",
        "bright_cyan": "\033[96m",
        "bright_white": "\033[97m",
        # Цвета для типов сообщений
        "info": "\033[94m",      # Синий
        "success": "\033[92m",   # Зеленый
        "warning": "\033[93m",   # Желтый
        "error": "\033[91m",     # Красный
    }
    
    @staticmethod
    def colorize(text: str, color: str) -> str:
        """
        Добавляет цвет к тексту.
        
        Args:
            text: Текст для окрашивания
            color: Название цвета
            
        Returns:
            Текст с ANSI кодами цветов
        """
        color_code = ConsoleOutput.COLORS.get(color, ConsoleOutput.COLORS["reset"])
        reset_code = ConsoleOutput.COLORS["reset"]
        return f"{color_code}{text}{reset_code}"
    
    @staticmethod
    def output(type_msg: str, message: str, program_name: str = "Shell", view_program: bool = False):
        """
        Выводит сообщение с цветом.
        
        Args:
            type_msg: Тип сообщения (info, success, warning, error)
            message: Текст сообщения
            program_name: Имя программы
            view_program: Показывать ли метку программы
        """
        colors = {
            "info": "\033[94m",  # Синий
            "success": "\033[92m",  # Зеленый
            "warning": "\033[93m",  # Желтый
            "error": "\033[91m",  # Красный
            "reset": "\033[0m",  # Сброс
        }

        normalized_type = (type_msg or "info").lower()
        color_code = colors.get(normalized_type, colors["reset"])
        reset_code = colors["reset"]
        label = normalized_type.upper().center(8)

        output_format = f"{color_code}[{label}] {program_name} > {message}{reset_code}" if view_program else f"{color_code}{message}{reset_code}"

        print(output_format)
