# Frontend architecture

Основний frontend KnowledgeHub побудований на Vue 3.

## Рівні

- `views/` — сторінки, що відповідають маршрутам.
- `components/` — повторно використовувані UI-компоненти.
- `api/` — HTTP-клієнт і предметні API-модулі.
- `composables/` — спільний реактивний стан і логіка.
- `styles/` — стабільні стилі Jinja-parity та нові стилі Vue-функцій.

## Collection workspace

`CollectionDetailView.vue` тепер є orchestration layer, а не великим монолітним компонентом.

Винесено:

- `CollectionHeader.vue`
- `CollectionEditDialog.vue`
- `CollectionDeleteDialog.vue`
- `DocumentSearchPanel.vue`
- `DocumentsList.vue`
- `DocumentUploadDialog.vue`
- `ResearchPanel.vue`
- `FeedbackMessages.vue`

Це дозволяє розвивати пошук, документи та RAG незалежно один від одного.
