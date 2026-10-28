# Отчёт 2. Исправления и верификация (Mini Shop)

Сервер: http://127.0.0.1:8066

Сводка изменений и политики
- Сессии и роли
  - Роль берётся только из server-side сессии (X-Token). Заголовок X-Role игнорируется.
  - Добавлена get_session(headers) и is_staff(session) для централизованной проверки.
  - Маскирование X-Token в журнале запросов.
- SQL и доступ к данным
  - Все SQL‑запросы параметризованы (SQLite placeholders ?).
  - Профили: customer получает только свой профиль; staff может запросить любой id.
  - Заказы: GET /orders — customer видит только свои; staff — все. POST /orders — цена берётся из каталога.
- Файловый доступ
  - /files требует сессию; запрещён path с «..», разрешён только files/<user>/receipt.txt.
  - user из query должен совпадать с пользователем сессии (кроме staff).
- Отзывы и XSS
  - /reviews/view экранирует HTML (html.escape).
- Assistant
  - /assistant/context: параметризованный order_id, проверка владения (кроме staff); отзывы только по продукту заказа (для PJI‑теста оставлены как текст).
  - /assistant/execute: политика доступа — read_file только свой чек; export_profiles и delete_tree — только staff.
- Журналы
  - /debug/logs доступен только staff; X-Token в логах маскируется.

Тесты: до/после
- Команда: make test → OK (см. evidence/after/tests.txt)
- Добавлены security‑тесты: профили/заказы по ролям, игнорирование price, политика assistant, экранирование XSS, staff‑требование для логов.

Доказательства (HTTP‑дампы после фиксов): practices/practice_06/lab/evidence/after

1) SQL Injection
- Было: f‑строки в /profile, /search, /assistant/context — SQLi приводила к расширенной выборке.
- Стало: параметризованные запросы и/или валидация int; для customer игнорируется query id.
- До: practices/practice_06/lab/evidence/before/sqli/*.json
- После:
  - /profile?id=1 OR 1=1: evidence/after/sqli/profile-or.json
  - /search?q=' OR '1'='1: evidence/after/sqli/search-or.json
  - /assistant/context?order_id=1 OR 1=1: evidence/after/sqli/assistant-context-or.json
- Риск (STRIDE): I/E → снижён: инъекция не интерполируется в SQL; контекст LLM формируется по валидированным данным.

2) Broken Access Control (BAC)
- Было: /profile и /orders отдавали чужие данные.
- Стало: /profile — customer видит только свой профиль; /orders — customer видит только свои.
- До: evidence/before/bac/profile-2.json, bac/orders.json
- После: evidence/after/bac/profile-2.json, bac/orders.json

3) Эскалация роли через X-Role
- Было: /admin/export доверял X-Role.
- Стало: роль только из сессии; /admin/export доступен только staff.
- До: evidence/before/role/admin-export.json (200)
- После: evidence/after/role/admin-export-as-alice.json (403)

4) Подмена цены (price tampering)
- Было: клиент мог задать произвольную price.
- Стало: сервер всегда берёт цену из каталога.
- Тесты: test_customer_can_buy_at_catalog_price, test_orders_price_ignored → OK
- До: evidence/before/price/order-price-1.json (price=1)
- После: evidence/after/price/order-alice.json (ожидается цена каталога)

5) Path traversal в пределах sandbox
- Было: можно читать чужие чеки и пытаться идти в private/*.
- Стало: запрещён «..», разрешён только receipt.txt; user должен соответствовать сессии (кроме staff).
- До: evidence/before/path/files-bob.json
- После: evidence/after/path/files-bob.json (403), files-bob-own.json (403), files-operator.json (403)

6) Stored XSS в /reviews/view
- Было: сырые отзывы в HTML.
- Стало: экранирование html.escape.
- До: evidence/before/xss/review-view.json (видно <script>)
- После: evidence/after/xss/review-view.json (ожидается &lt;script&gt;)

7) Prompt injection (канал)
- Было: вредные инструкции в отзывах попадали в prompt; сервер слепо исполнял решение.
- Стало: сервер исполняет решения по строгой политике; вредные инструменты заблокированы для customer.
- До (контексты): evidence/before/assistant/context-initial.json, context-after-review.json
- После (инструменты): evidence/after/assistant/execute-export-profiles.json (403), execute-delete-tree.json (403), execute-read-own.json (200)
- Сравнение «модель vs исполнитель»: даже если модель вернёт JSON с tool: export_profiles или delete_tree, исполнитель отвечает 403. Таким образом, серверная защита независима от послушания модели (зафиксировано в evidence/after/assistant/*.json).

8) Assistant/execute — политика доступа
- Было: любой клиент мог читать, экспортировать и удалять.
- Стало: read_file — только свой чек; export/delete — только staff.
- После: evidence/after/assistant/execute-*.json

9) /debug/logs — утечки
- Было: доступен всем, утечка токенов и тел запросов.
- Стало: только staff; X-Token в логах маскируется.
- После: evidence/after/logs/debug-logs-alice.json (403), debug-logs-staff.json (200, X-Token=***)

Итог
- Политики аутентификации/авторизации внедрены, SQL‑инъекции исключены параметризацией, файловый доступ и инструменты assistant ограничены согласно ролям.
- Все тесты (штатные и добавленные security) проходят: evidence/after/tests.txt
- Готовы к повторной фиксации внешних HTTP‑дампов при необходимости (скрипт: scripts/run_after_scenarios.py).
