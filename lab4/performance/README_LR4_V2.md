# KnowledgeHub — LR4 Performance Experiment V2

## Мета

Порівняти продуктивність конкретних операцій KnowledgeHub у двох середовищах:

1. Localhost
2. Railway production

Тестуються різні види серверної роботи, а не лише один GET-запит.

## Сценарії

### 1. Health

`GET /api/v1/health`

Характеризує базову мережеву та application latency без авторизації і без читання прикладних даних.

### 2. Collections

`GET /api/v1/collections`

Authenticated request. Включає перевірку server-side session та читання колекцій користувача з PostgreSQL.

### 3. Documents

`GET /api/v1/collections/{collection_id}/documents`

Authenticated request. Включає session authentication, ownership collection та читання списку документів з PostgreSQL.

### 4. Lexical search

`GET /api/v1/collections/{collection_id}/search?q=...&mode=lexical&limit=10`

Authenticated request. Включає session authentication, ownership та PostgreSQL Full Text Search.

Semantic/hybrid режими не входять до порівняння Localhost/Railway, оскільки lightweight Railway profile вимикає ML-функціональність. Для коректного порівняння використовується функція, доступна в обох середовищах.

## Навантаження

Для кожного сценарію:

- 1 VU
- 10 VU
- 25 VU
- 15 секунд
- 3 повтори
- `sleep(1)` між ітераціями

Загальна кількість запусків:

2 середовища × 4 сценарії × 3 рівні VU × 3 повтори = 72 запусків.

`sleep(1)` означає, що `req/s` характеризує контрольований workload, а не максимальну пропускну здатність сервера.

## Метрики

Використовуються custom k6 metrics лише для вимірюваного endpoint:

- `target_req_duration`
- `target_reqs`
- `target_req_failed`
- `target_checks_success`

Це важливо, тому що CSRF/login у setup потрібні для authentication, але їхня latency не змішується з latency операції, яку тестуємо.

Для таблиць збираються:

- Avg, ms
- Median, ms
- p90, ms
- p95, ms
- p99, ms
- req/s
- Error, %
- Checks success, %

## Підготовка даних

У Localhost та Railway потрібно створити окремого test user та колекцію `Performance Test`.

В обидві колекції слід завантажити однаковий набір fixture-файлів.

Перед запуском зафіксувати:

- Localhost user email/password
- Localhost collection ID
- Railway user email/password
- Railway collection ID

Паролі не записуються у файли. Runner запитує їх через `Read-Host -AsSecureString`.

## Запуск

1. Запустити локальний FastAPI backend.
2. Переконатися, що Railway deployment доступний.
3. Перейти до:

`lab4/performance/scripts`

4. Виконати:

```powershell
.\run_lab4_v2.ps1
```

Runner запитає credentials та collection IDs.

## Результат

Створюється каталог:

`lab4/performance/results/<timestamp>_v2/`

У ньому:

- `raw/*.json` — k6 summary кожного запуску
- `lab4_v2_results.csv` — усі 72 запусків
- `lab4_v2_summary.csv` — середні значення трьох повторів

`results/` повинен залишатися в `.gitignore`.

## Методологічне обмеження

Цей експеримент не визначає абсолютну максимальну продуктивність KnowledgeHub.

Він порівнює latency, стабільність та фактичний throughput чотирьох конкретних операцій у контрольованому навантажувальному сценарії.
