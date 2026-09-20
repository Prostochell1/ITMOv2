# Unit-проверки

| Требование или правило | Что проверяем изолированно | Вход | Ожидаемый результат | Evidence |
|---|---|---|---|---|
| Формирование промпта | `ReviewService.review` строит строку промпта | diff="ABC" | Строка начинается с "Review this pull request and find problems:\nABC" и вызывает LLM.generate | app/review_service.py:19–21 |
| Формат ответа | Возврат словаря с ключом `comment` | answer="ok" | Возвращается {"comment": "ok"} | app/review_service.py:21–22 |

## Как использовали AI

- Строка в [`prompts.md`](prompts.md): P1-02
- Что проверили и исправили сами: Сопоставили сигнатуры и формат с diff; исключили внеконтекстные проверки.
