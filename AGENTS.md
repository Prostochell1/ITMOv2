AGENTS.md — маршрут для работы агента с питон‑проектом practice_03

Цель
- Вносить изменения только в учебный сервис Notify Mini, расположенный в practices/practice_03/lab/demo, и проверять их стандартными командами проекта.

Контекст проекта
- Язык/окружение: Python 3.10+, стандартная библиотека. Без внешних зависимостей.
- Рабочая ОС: рекомендуется WSL (bash/zsh), допустим запуск из Linux/macOS.
- Структура:
  - practices/practice_03/README.md — описание практики и общие правила.
  - practices/practice_03/Makefile — проксирует install/test в lab/.
  - practices/practice_03/lab/Makefile — проверка версии Python и запуск тестов демо.
  - practices/practice_03/lab/demo/README.md — краткое описание сервиса.
  - practices/practice_03/lab/demo/service.py — целевой код сервиса.
  - practices/practice_03/lab/demo/test_service.py — юнит‑тесты.
  - practices/practice_03/lab/demo/Makefile — команда тестов.
  - practices/practice_03/lab/demo/opencode.json — конфигурация OpenCode для демо.

Команды запуска и проверки
- Из корня репозитория:
  - make test — запустит тесты демо через вложенные Makefile.
- Точечный запуск для демо:
  - make -C practices/practice_03/lab/demo test
- Альтернативно (внутри папки practices/practice_03/lab/demo):
  - python3 -m unittest -v
- Быстрая проверка окружения (Python 3.10+):
  - make -C practices/practice_03/lab install

Границы изменений
- Разрешено:
  - Править только код сервиса в practices/practice_03/lab/demo/service.py.
  - При необходимости добавлять вспомогательные функции/константы в этом же файле, не меняя публичный контракт функции subscribe.
- Запрещено без отдельного указания:
  - Менять tests: practices/practice_03/lab/demo/test_service.py.
  - Менять Makefile‑файлы и структуру каталогов.
  - Добавлять внешние зависимости (requirements, pip и т.п.).

Интерфейс и требования к поведению
- Функция subscribe(name: str) должна:
  - Отклонять пустые/пробельные значения: raise ValueError("empty name").
  - Добавлять уникальные имена в глобальное множество subscribers (без дублей).
  - Возвращать словарь {"subscribed": True} при успешной подписке.

Условие приёмки (A)
- Все тесты в practices/practice_03/lab/demo/test_service.py проходят локально: make -C practices/practice_03/lab/demo test завершается с кодом 0 и выводом успешных тестов.
- При повторной подписке одного и того же имени размер множества subscribers не увеличивается.
- Запуск make -C practices/practice_03/lab install подтверждает Python 3.10+.

Быстрый маршрут для агента
1) Прочитай файлы проекта (README/Makefile/test_service.py/service.py) в practices/practice_03/lab/demo.
2) Внеси изменения ТОЛЬКО в service.py в рамках описанного контракта.
3) Проверь: make -C practices/practice_03/lab/demo test (или make test из корня).
4) Если тесты зелёные — работа выполнена; иначе откати/исправь правки в пределах указанной области.

Проверка чтения (self‑check)
- Найди и перечисли пути к ключевым файлам: service.py, test_service.py, Makefile’ы в трёх уровнях (practice_03, lab, demo), README.md для демо.
- Перечисли применимые ограничения: без внешних зависимостей, не менять тесты/Makefile/структуру, Python 3.10+, редактировать только service.py, сохранить контракт subscribe.
- Назови точные команды для проверки и из какого каталога их запускать.

Ссылки на артефакты
- practices/practice_03/README.md
- practices/practice_03/Makefile
- practices/practice_03/lab/Makefile
- practices/practice_03/lab/demo/README.md
- practices/practice_03/lab/demo/service.py
- practices/practice_03/lab/demo/test_service.py
- practices/practice_03/lab/demo/Makefile
- practices/practice_03/lab/demo/opencode.json

Skill: TDD (Test-Driven Development)
- Используемый skill: skills/tdd/SKILL.md (локальная копия) и supporting-files каталога от skills use.
- Seam под тестирование: публичная функция subscribe(name) и наблюдаемое множество subscribers.
  - Что покрывает: поведение добавления уникальных имён, отказ на пустых значениях, отсутствие дубликатов — проверяется через публичный интерфейс и состояние.
  - Что не покрывает: внутренние детали реализации (структуры данных, порядок вызовов), любые побочные эффекты вне интерфейса.
- Правило: писать/изменять тесты только по отдельному указанию. При разрешении — работать вертикальными слайсами (один тест → минимальная реализация → повтор), не привязываясь к деталям реализации, и проверять через публичный интерфейс.
- Подсказки из skills/tdd/tests.md и skills/tdd/mocking.md: избегать тестов, завязанных на детали реализации; мокать только системные границы.

Style Guide (этап 4.1)
- Источник: PEP 8 (https://peps.python.org/pep-0008/) и PEP 257 (https://peps.python.org/pep-0257/), целевая версия Python 3.10.
- Короткая выжимка правил (применимых к этой задаче):
  1) Докстроки для публичных функций (PEP 257): каждая публичная функция в service.py должна иметь краткую докстроку с однострочным описанием. Пример: def count(): """Return the number of unique subscribers."""
  2) Именование (PEP 8): функции и переменные — snake_case; константы — UPPER_CASE. Пример: list_subscribers, subscribers.
  3) Пустые строки (PEP 8): между верхнеуровневыми функциями — одна пустая строка. Без лишних пустых строк внутри простых функций.
  4) Длина строки (PEP 8): стараться не превышать 79 символов.
- Когда читать гайд: перед любыми изменениями в practices/practice_03/lab/demo/service.py.
- Где применяется: файл practices/practice_03/lab/demo/service.py. Проверьте, что все публичные функции имеют докстроки, соблюден snake_case и формат пустых строк.

Ссылка на файл выдержки: practices/practice_03/lab/demo/STYLEGUIDE.md
