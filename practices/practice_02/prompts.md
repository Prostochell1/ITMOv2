# Журнал экспериментов Практики 2

- Выбранный слабый артефакт Практики 1: practices/practice_01/project_management.md
- Что в нём нужно улучшить: конкретизировать даты (YYYY-MM-DD), владельцев (человек/AI), зависимости между инкрементами и проверяемые результаты со ссылками на файлы Практики 1 и правила из CASE.md (SEC-1, API-1, REL-1, SCOPE-1, QA-1, OUT-1, OBS-1).
- Как поймём, что изменение полезно: план станет воспроизводимым — для каждого инкремента есть дата-диапазон, владелец, зависимость и проверка с явной ссылкой (на tests_*.md, analysis.md, adr.md, prompts.md P1-02 или правило CASE.md). Диаграмма Ганта совпадает с таблицей.

| Техника | Файл эксперимента | Изменённый файл Практики 1 | Конкретное изменение | Проверка | Что отклонили |
|---|---|---|---|---|---|
| Few-shot | [`few_shot/experiment.md`](few_shot/experiment.md) | practices/practice_01/project_management.md | Уточнили даты, роли, зависимости; синхронизировали Гант | Ссылки на tests_* и CASE (API-1, REL-1, QA-1) | Общие формулировки без ссылок |
| R.C.T.F. | [`rctf/experiment.md`](rctf/experiment.md) | practices/practice_01/project_management.md | Переформатировали план по RCTF с явными проверками | Сопоставили проверки с tests_* и правилами CASE | Изменение API-контракта (против ADR) |
| Chain of Verification | [`chain_of_verification/experiment.md`](chain_of_verification/experiment.md) | practices/practice_01/project_management.md | Добавили зависимость 2→1 и ссылки на API-1 в Инкременте 3 | Таблица вопросов и evidence | Утверждения без источников |
| Tree of Thoughts | [`tree_of_thoughts/experiment.md`](tree_of_thoughts/experiment.md) | practices/practice_01/project_management.md | Выбрали альтернативу B (ранний e2e), обновили содержание Инкремента 2 | Ссылки на tests_e2e.md, tests_unit.md, tests_integration.md | Нагрузка до базовых тестов |
| RAG | [`rag/experiment.md`](rag/experiment.md) | practices/practice_01/project_management.md | Добавили точечные дельты с цитатами источников | Таблица «Изменение | Источник | Обоснование» | Предложения без evidence |
| ReAct | [`react/experiment.md`](react/experiment.md) | practices/practice_01/project_management.md | Применили дельты после 6 шагов действий/валидации | Таблица шагов; сопоставление дат | Идеи без валидации по CASE/tests_*.md |

## Независимое ревью

| Замечание другой команды | Где исправили | Evidence |
|---|---|---|
| Двусмысленность |  |  |
| Непроверяемое требование |  |  |
| Пропущенный риск или источник |  |  |
