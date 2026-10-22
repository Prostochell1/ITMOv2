Style Guide (для Notify Mini)

Источник(и):
- PEP 8 — Style Guide for Python Code: https://peps.python.org/pep-0008/
- PEP 257 — Docstring Conventions: https://peps.python.org/pep-0257/

Версия окружения: Python 3.10+

3–5 правил, используемых в этом проекте
1) Докстроки для публичных функций (PEP 257)
   - Требование: каждая публичная функция должна иметь однострочную докстроку, описывающую назначение.
   - Пример: 
     def count():
         """Return the number of unique subscribers."""

2) Именование в snake_case (PEP 8)
   - Функции/переменные — snake_case; константы — UPPER_CASE.
   - Пример: list_subscribers, subscribers.

3) Организация пустых строк (PEP 8)
   - Между верхнеуровневыми функциями — одна пустая строка.
   - Не добавлять лишние пустые строки внутри коротких функций.

4) Длина строки (PEP 8)
   - Стараться не превышать 79 символов в строке.

Применение
- Этот стиль обязателен для файла practices/practice_03/lab/demo/service.py.
- Проверяйте соответствие перед коммитом и запуском тестов.
