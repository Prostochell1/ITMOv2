# Mini Shop — инвентаризация API и гипотезы уязвимостей

Ниже перечислены эндпоинты по коду service.py с параметрами, гипотезами уязвимостей, примерами для проверки, планом и ожидаемыми индикаторами.

Примечания: RCE отсутствует; sandbox ограничивает физический вывод за пределы временного каталога, но логические проверки доступа отсутствуют.

| Метод/Путь | Параметры | Гипотеза уязвимости | План проверки (пример инпута/заголовков) | Ожидаемый индикатор |
|---|---|---|---|---|
| GET /health | — | Нет | GET /health | 200 {"status":"ok"} |
| GET /products | — | Нет | GET /products | 200 каталог |
| POST /login | body: username,password | Утечка через /debug/logs | 1) POST /login {"username":"alice","password":"learn-alice"} 2) GET /debug/logs | В логах виден пароль/токен |
| GET /profile | query: id | SQLi; BAC | SQLi: GET /profile?id=1 OR 1=1; BAC: без токена запросить id=2 | Возвращаются оба профиля; данные bob видны без auth |
| GET /search | query: q | SQLi; утечка | GET /search?q=' OR 1=1 -- (URL-экранировать) | Все профили в ответе |
| GET /orders | — | BAC/утечка | GET /orders без токена | Все заказы видны |
| POST /orders | headers: X-Token; body: product,[price] | Price tampering | POST /orders {"product":"lamp","price":1} + X-Token | 201 и price: 1 |
| GET /admin/export | headers: X-Role | Роль через X-Role; BAC | GET /admin/export с X-Role: staff (без токена) | 200 и список профилей |
| GET /files | query: user,path | BAC; path traversal в пределах sandbox | Чужой чек: /files?user=bob&path=receipt.txt; Traversal: /files?user=alice&path=../../private/operator-note.txt | Получение чека bob; утечка TEST_ONLY_OPERATOR_SECRET |
| POST /reviews | body: product,text | XSS (stored); LLM prompt injection канал | POST /reviews {"product":"chair","text":"</p><script>alert(1)</script>"} | Далее /reviews/view содержит <script> |
| GET /reviews/view | — | XSS | После выше: GET /reviews/view | Сырой HTML со вставкой |
| GET /debug/logs | — | Утечки (токены/пароли/тела) | После логина/заказа: GET /debug/logs | Видно X-Token, пароли, тела |
| GET /assistant/context | query: order_id,question | BAC; prompt injection канал | BAC: /assistant/context?order_id=2 (без токена); Prompt inj: после POST /reviews с вредным текстом | Prompt содержит заказ bob; отзыв включён как текст |
| POST /assistant/execute | body: {decision:{tool,arguments}} | Инструменты без auth/ACL; BAC; DoS | read_file: path=private/operator-note.txt; export_profiles; delete_tree: path='.' | 200 с секретом; профили; подтверждение удаления |

Ссылки: см. также диаграмму и STRIDE в [model.md](./model.md).
