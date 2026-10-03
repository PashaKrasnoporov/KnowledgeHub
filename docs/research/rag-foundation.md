# RAG foundation

## Мета

Відокремити retrieval від майбутньої генеративної моделі та забезпечити прозорі джерела.

## Endpoint

`GET /api/v1/collections/{collection_id}/research`

Параметри:

- `q` — запитання користувача;
- `limit` — кількість контекстних фрагментів, 1–10.

## Retrieval

Використовуються вже збережені `document_chunks`.

Для кожного chunk:

- semantic score — cosine-like similarity через нормалізовані embeddings;
- lexical score — перекриття інформативних токенів;
- combined score — `0.75 * semantic + 0.25 * lexical`.

Для різноманітності контексту використовується максимум два фрагменти з одного документа.

## Поточна відповідь

Поточний етап не викликає зовнішню LLM.

Система формує extractive draft:

- відбирає речення з найрелевантніших фрагментів;
- ранжує їх відносно запитання;
- додає номер джерела;
- повертає текстові фрагменти та scores.

## Наступний етап

Після цього retrieval layer можна передати LLM:

`question + ranked sources -> prompt -> generated answer with citations`.

Це не потребуватиме зміни існуючого індексування документів.
