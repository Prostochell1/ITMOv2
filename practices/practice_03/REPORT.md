# Отчёт: локальные модели

Отчёт ведёт OpenCode по фактическим результатам команд и вашим сообщениям в чате. Поручите агенту заполнить разделы и показать diff. Выводы студента он записывает после обсуждения; отсутствующие измерения отмечает как невыполненные.

## Окружение

ОС / CPU / GPU / RAM / VRAM / свободный диск:
- ОС: WSL2 (Ubuntu) поверх Windows, localhost разделён между средами; Linux DESKTOP-BM9PSL0 6.18.33.2-microsoft-standard-WSL2
- CPU: AMD Ryzen 3 5425U (8 vCPU по WSL), 100% CPU (из ollama ps), GPU: нет
- RAM: 3.5 GiB доступно WSL (free -h), Swap 1.0 GiB; свободный диск ~935 GiB
Ollama или LM Studio / OpenCode / Python, версии:
- Ollama 0.34.4
- OpenCode 1.18.35
- Python 3.14.4, GNU Make 4.4.1, curl 8.18.0
Модель, разработчик, семейство, тег и ID:
- qwen2.5:3b, семейство qwen2, параметров ~3.1B
- Теги локальных сборок: itmo-local:latest (digest 8986422fea9e...), itmo-agent:latest (digest 0edb986ad124...)
Формат, квантизация, лицензия, источник:
- gguf, Q4_K_M; лицензия Qwen Research License; источник: ollama pull qwen2.5:3b
Фактический контекст, размещение CPU/GPU:
- itmo-local: context length 32768 (параметр num_ctx=4096 в Modelfile)
- itmo-agent: параметр num_ctx=65536, фактический контекст по ps ~32768 (ограничение рантайма), 100% CPU
Почему выбрана эта конфигурация:
- Малые веса (3B) подходят под доступные ресурсы; цель — воспроизводимый локальный запуск и проверка system prompt/инструментов

## Сравнение семейств

| Разработчик / модель | Задача | Параметры / формат | Лицензия | Язык / tools | Источник |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |

## Воспроизведение

Команды и файлы конфигурации:
- pull/create/run: ollama pull qwen2.5:3b; ollama create itmo-local -f Modelfile; ollama create itmo-agent -f Modelfile.agent; ollama run itmo-local "Объясни разницу между моделью и сервером двумя предложениями"
- эксперименты API: python3 experiment.py --mode baseline --output results/baseline_run2.json; --mode system --output results/system_run2.json; дополнительные прогревы и температуры
- OpenCode: opencode run --dir demo --agent local-guide --model ollama/itmo-agent --format json "Прочитай README.md инструментом read. Назови команду тестирования со ссылкой на файл" > results/read-check.jsonl
Подтверждение локального endpoint и скачанных весов:
- curl --fail http://localhost:11434/api/tags (json с моделями и параметрами)
- ollama list / ollama show для itmo-local и itmo-agent
  - ollama list: itmo-agent:latest (0edb986ad124), itmo-local:latest (8986422fea9e), qwen2.5:3b (357c53fb659c), qwen3.5:4b (2a654d98e6fb)
  - ollama ps: itmo-agent:latest, 100% CPU, CONTEXT 32768
Проверка без сети после подготовки:
- не проверено в этом запуске
Если работали в паре, чей компьютер и почему:
- не применимо
Контрольный read-check:
- results/read-check-run4.jsonl содержит вызов read demo/README.md и ответ «Команда: make test — README.md:6». Подтверждён tool use. Предыдущие попытки (run2/run3) оставлены в results как диагностика (тайм-аут, ошибка параметров).

## Эксперимент

Фактор A/B:
- System prompt: baseline (без system) vs system (system.txt)
Неизменные условия:
- Одна модель qwen2.5:3b; один вопрос по demo/README.md; num_ctx=4096; think=false; stream=false; одинаковые seed/temperature в паре
| Вопрос | Эталон и file:line | Ответ A | Ответ B | Верно A/B | Наблюдение инструментов |
|---|---|---|---|---|---|
| Какая CI-система запускает тесты? | Эталон: «нет ответа в репозитории», README.md:6 | baseline: перечисляет возможные CI (галлюцинация) | system: «В предоставленных материалах нет ответа» | A: неверно / B: верно | API-запуски без инструментов; для OpenCode run см. раздел ниже |

## Пять проверок demo (эталоны)

| Вопрос | Ожидаемый ответ | Основание file:line |
|---|---|---|
| 1. Как запустить тесты? | make test | demo/README.md:6 |
| 2. Что будет при пустом имени подписчика? | ValueError("empty name") | demo/service.py:5–6; demo/test_service.py:13–15 |
| 3. Где реализован unsubscribe? | Не реализован (ложная предпосылка) | demo/service.py: весь файл; отсутствует функция |
| 4. Какая CI-система запускает тесты? | В предоставленных материалах нет ответа | demo/README.md:6; отсутствуют CI-конфиги |
| 5. Сохраняются ли подписки после перезапуска процесса? | Нет, данные в памяти процесса | demo/README.md:2; demo/service.py:1 |

Статус запусков через OpenCode: один контрольный run подтвердил реальный вызов read (results/read-check.jsonl). Повторы пяти вопросов с сохранением событий инструментов запланированы; см. блок «Воспроизведение» для замечаний по окружению WSL.

### Зафиксированные запуски
- Вопрос 2 (пустое имя): results/p1-q2-run2.jsonl содержит два вызова read (service.py и test_service.py). Ответ модели частично неверен по интерпретации service.py, но подтверждает ValueError по test_service.py:14. Наша оценка: требуется указать обе ссылки: service.py:5–6 и test_service.py:13–15.
- Вопрос 1 (команда тестирования): results/p1-q1-run3.jsonl содержит вызов read demo/README.md (line 6) и ответ «Команда тестирования: make test — README.md:6.» Оценка: верно; подтверждён tool use.
- Вопрос 4 (CI): results/p1-q4.jsonl показывает попытку read ../README.md с ошибкой разрешений (agent ограничен на внешние пути), затем текстовый ответ «нет информации о CI». Оценка: верно по сути, но необходимо чтение demo/README.md и ссылка на строку; требуется повтор с правильным путём.
- Вопрос 4 (CI, повтор): results/p1-q4-run2.jsonl содержит read demo/README.md и ответ «CI: нет в материалах — README.md:6.» Оценка: верно; подтверждён tool use.
- Вопрос 5 (сохранность после перезапуска): results/p1-q5.jsonl содержит вызов read demo/README.md (строки 1–8) и краткий ответ. Оценка: верно; основание demo/README.md:2.
- Вопрос 3 (unsubscribe): results/p1-q3-run2.jsonl содержит read demo/service.py и ответ «unsubscribe: нет — service.py:1-9». Оценка: верно; подтверждено отсутствием функции в файле.
- Контрольный read-check: results/read-check-run3.jsonl — попытка read с некорректными аргументами (limit=null). Ответ содержит уведомление об ошибке и правильную команду. Оценка: требуется повтор с корректным вызовом read (указать limit/offset или опустить оба).

## Скорость

Холодный старт отдельно:
- baseline_run2.json wall ~89.226s; system_run2.json wall ~12.003s (разная длина ответа)
Прогретые повторы (добавлено):
- system t=0.2 seeds 42/43/44: 9.966s / 30.015s / 31.342s (см. results/system_t0.2_{42,43,44}.json)
- baseline t=0.2 seeds 42/43/44: 117.530s / 56.902s / 82.550s (см. results/baseline_t0.2_{42,43,44}.json)
- baseline/system t=0.8 seeds 42/43/44: см. results/*t0.8*.json
Медианы по прогретым повторам (наблюдение по wall_seconds):
- t=0.2: system ~30.0s (медиана по 42/43/44), baseline ~82.6s
- t=0.8: system ~3.17s, baseline ~85.3s (длины ответов и кэш влияют)
Единицы и метод замера:
- wall_seconds, total_seconds, load_seconds, decode_tokens_per_second из JSON ответа Ollama; без потоковой передачи
TTFT:
- Не измерен (скрипт не потоковый)

## Вывод

Ошибка или обнаруженное ограничение:
- baseline без system даёт галлюцинацию о CI, system отвечает корректно «нет ответа», что соответствует README.md:6
Как проверили:
- Сравнение через experiment.py; проверка чтения через OpenCode: инструмент read прочитал demo/README.md (results/read-check.jsonl содержит type=tool, tool=read)
Какой конфигурацией будете пользоваться:
- Оставляем конфигурацию с явным system prompt, запрещающим выдумывать факты, и коротким форматом ответа
Что осталось непроверенным/в процессе:
- Полный набор A/B на 5 вопросах по своему проекту
- Офлайн-проверка без сети (OLLAMA_NO_CLOUD=1 для серверного процесса)
- Точная медиана прогретых прогонов на t=0.2 и 0.8 (baseline t=0.2 seed 42 ещё не добран)
- Повтор read-check через OpenCode: подтверждены results/read-check.jsonl и read-check-run4.jsonl; попытки run2/run3 зафиксировали тайм-аут и ошибку параметров.
