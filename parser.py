class ShellParser:
    # Определите операторы перенаправления как константу
    REDIRECT_OPERATORS = {">>", ">&", "<&", "<>", "<<", ">>>", "<", ">", "2>"}

    @staticmethod
    def tokenize(command_line: str = ""):
        """
        Токенизирует командную строку, учитывая:
        - пробелы как разделители
        - одинарные и двойные кавычки
        - экранирование символов
        - операторы перенаправления как отдельные токены
        """
        tokens = []
        current_token = ""
        in_single_quote = False
        in_double_quote = False
        escape_next = False

        i = 0
        while i < len(command_line):
            char = command_line[i]

            # Обработка экранирования
            if escape_next:
                current_token += char
                escape_next = False
                i += 1
                continue

            if char == "\\":
                # Экранирование следующего символа
                escape_next = True
                i += 1
                continue

            # Проверяем, начинается ли здесь оператор перенаправления
            # Только если мы не внутри кавычек
            if not (in_single_quote or in_double_quote):
                # Проверяем двухсимвольные операторы
                if i + 1 < len(command_line):
                    two_char_op = command_line[i : i + 2]
                    if two_char_op in ShellParser.REDIRECT_OPERATORS:
                        # Если текущий токен собран, добавляем его
                        if current_token:
                            tokens.append(current_token)
                            current_token = ""
                        # Добавляем оператор как отдельный токен
                        tokens.append(two_char_op)
                        i += 2  # Пропускаем два символа оператора
                        continue
                # Проверяем односимвольные операторы
                if char in ShellParser.REDIRECT_OPERATORS:
                    # Если текущий токен собран, добавляем его
                    if current_token:
                        tokens.append(current_token)
                        current_token = ""
                    # Добавляем оператор как отдельный токен
                    tokens.append(char)
                    i += 1  # Пропускаем один символ оператора
                    continue

            # Обработка кавычек
            if char == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
            elif char == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
            # Обработка пробелов (разделителей)
            elif char == " " and not (in_single_quote or in_double_quote):
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            else:
                current_token += char

            i += 1

        # Добавляем последний токен, если он есть
        if current_token:
            tokens.append(current_token)

        return tokens
