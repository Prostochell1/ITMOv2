# E2E-проверки

| Сценарий пользователя | Предусловия | Действие | Наблюдаемый результат | Evidence |
|---|---|---|---|---|
| Позитивный | Сервис запущен; подставлен стаб LLM, возвращающий "OK" | POST `/api/reviews` с телом `{"diff": "diff --git a/x b/x\n..."}` | 200 OK, JSON содержит ключ `comment` (не пустой) | TRAINING_PR.diff: app/api.py:35–38; app/review_service.py:19–22 |
| Негативный (отсутствует diff) | Сервис запущен | POST `/api/reviews` с телом `{}` | AS IS: 500 (KeyError). TO BE: 422/400 с сообщением "diff required" | app/api.py:36–38 — `payload["diff"]` без проверки |
| Граничный (слишком длинный diff) | Сервис запущен | POST `/api/reviews` с `diff` длиной 20 001 символ | AS IS: неопределённо (возможен 200/5xx). TO BE: 413 Payload Too Large | CASE.md: API-1 (лимит 20 000 символов) |

## Как использовали AI

- Строка в [`prompts.md`](prompts.md): P1-02, Master Prompt v1
- Что проверили и исправили сами: Сопоставили сценарии с diff и правилами CASE (API-1); уточнили ожидаемое поведение AS IS vs TO BE.
