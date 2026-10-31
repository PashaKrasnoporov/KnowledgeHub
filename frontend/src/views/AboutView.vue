<script setup>
const SYSTEM_VERSION = "v1"

const capabilities = [
    {
        title: "Колекції",
        text: "Створюйте окремі простори для навчальних дисциплін, проєктів, досліджень або інших тем."
    },
    {
        title: "Документи",
        text: "Завантажуйте PDF, DOCX і TXT, переглядайте вміст та зберігайте матеріали у потрібній колекції."
    },
    {
        title: "Пошук",
        text: "Використовуйте lexical, semantic і hybrid режими для точних та змістовно близьких результатів."
    },
    {
        title: "Quick Search",
        text: "Шукайте текст у локальних TXT, PDF і DOCX без реєстрації. Файл обробляється безпосередньо у браузері."
    },
    {
        title: "AI / RAG",
        text: "У повній локальній конфігурації KnowledgeHub підтримує інтелектуальну роботу з контекстом документів і RAG-сценарії."
    },
    {
        title: "Безпека",
        text: "Доступ до колекцій і документів контролюється автентифікацією, перевіркою власника ресурсу та CSRF-захистом."
    }
]

const steps = [
    {
        number: "01",
        title: "Створіть колекцію",
        text: "Організуйте матеріали за предметом, проєктом або напрямом роботи."
    },
    {
        number: "02",
        title: "Додайте документи",
        text: "Завантажте PDF, DOCX або TXT вручну чи перетягуванням."
    },
    {
        number: "03",
        title: "Виконайте пошук",
        text: "Сформулюйте запит і виберіть режим пошуку відповідно до задачі."
    },
    {
        number: "04",
        title: "Повертайтеся до матеріалів",
        text: "Використовуйте блок «Нещодавні» для швидкого доступу до останніх колекцій і документів."
    }
]

const searchModes = [
    {
        name: "Lexical",
        badge: "Точні збіги",
        text: "Шукає слова та фрази, що безпосередньо присутні у документі. Підходить для назв, термінів і конкретних формулювань."
    },
    {
        name: "Semantic",
        badge: "За змістом",
        text: "Порівнює зміст запиту і документів за embedding-представленнями та може знаходити релевантний текст без точного збігу слів."
    },
    {
        name: "Hybrid",
        badge: "Комбінований",
        text: "Поєднує lexical і semantic підходи, враховуючи одночасно ключові слова та змістову близькість."
    }
]
</script>

<template>
    <section class="about-page">
        <header class="about-hero">
            <div class="about-hero-copy">
                <p class="eyebrow">
                    ABOUT KNOWLEDGEHUB
                </p>

                <h1>
                    Про KnowledgeHub
                </h1>

                <p class="about-lead">
                    KnowledgeHub — персональна платформа для організації
                    колекцій документів, пошуку інформації та подальшої
                    інтелектуальної роботи з власною базою знань.
                </p>

                <div class="about-meta">
                    <span class="version-badge">
                        Версія {{ SYSTEM_VERSION }}
                    </span>

                    <span>
                        Активна розробка
                    </span>
                </div>
            </div>

            <aside class="about-purpose-card">
                <span class="about-purpose-label">
                    ГОЛОВНА ІДЕЯ
                </span>

                <strong>
                    Менше часу на пошук матеріалів — більше на роботу з ними.
                </strong>

                <p>
                    Система об'єднує зберігання, навігацію,
                    пошук та AI-інструменти в одному просторі.
                </p>
            </aside>
        </header>

        <section class="about-section">
            <div class="about-section-heading">
                <p class="eyebrow">
                    CAPABILITIES
                </p>

                <h2>
                    Основні можливості
                </h2>

                <p>
                    KnowledgeHub охоплює повний цикл роботи:
                    від додавання матеріалу до його пошуку
                    та повторного використання.
                </p>
            </div>

            <div class="about-card-grid">
                <article
                    v-for="item in capabilities"
                    :key="item.title"
                    class="about-card"
                >
                    <h3>
                        {{ item.title }}
                    </h3>

                    <p>
                        {{ item.text }}
                    </p>
                </article>
            </div>
        </section>

        <section class="about-section">
            <div class="about-section-heading">
                <p class="eyebrow">
                    GETTING STARTED
                </p>

                <h2>
                    Як почати роботу
                </h2>

                <p>
                    Для більшості сценаріїв достатньо
                    чотирьох послідовних кроків.
                </p>
            </div>

            <div class="workflow-grid">
                <article
                    v-for="step in steps"
                    :key="step.number"
                    class="workflow-step"
                >
                    <span class="workflow-number">
                        {{ step.number }}
                    </span>

                    <h3>
                        {{ step.title }}
                    </h3>

                    <p>
                        {{ step.text }}
                    </p>
                </article>
            </div>
        </section>

        <section class="about-section">
            <div class="about-section-heading">
                <p class="eyebrow">
                    SEARCH MODES
                </p>

                <h2>
                    Режими пошуку
                </h2>

                <p>
                    Вибір режиму залежить від того, чи потрібен
                    точний збіг, змістова подібність або
                    комбінація обох підходів.
                </p>
            </div>

            <div class="search-mode-grid">
                <article
                    v-for="mode in searchModes"
                    :key="mode.name"
                    class="search-mode-card"
                >
                    <div class="search-mode-header">
                        <h3>
                            {{ mode.name }}
                        </h3>

                        <span>
                            {{ mode.badge }}
                        </span>
                    </div>

                    <p>
                        {{ mode.text }}
                    </p>
                </article>
            </div>

            <p class="deployment-note">
                Доступність semantic, hybrid та AI/ML-функцій
                залежить від конфігурації розгортання.
                Полегшений хмарний профіль може працювати
                з обмеженим набором функцій.
            </p>
        </section>

        <section class="about-two-column">
            <article class="about-info-panel">
                <p class="eyebrow">
                    PRIVACY & SECURITY
                </p>

                <h2>
                    Приватність і безпека
                </h2>

                <p>
                    Колекції та документи користувача доступні
                    лише після автентифікації та перевірки
                    прав доступу. Для операцій зміни даних
                    застосовується CSRF-захист.
                </p>

                <p>
                    Quick Search працює окремо: локальний файл
                    аналізується у браузері й не завантажується
                    до бази KnowledgeHub.
                </p>
            </article>

            <article class="about-info-panel">
                <p class="eyebrow">
                    DEVELOPMENT
                </p>

                <h2>
                    Куди розвивається система
                </h2>

                <div class="roadmap-line">
                    <span>V1</span>
                    <span class="roadmap-arrow">→</span>
                    <span>V2</span>
                    <span class="roadmap-arrow">→</span>
                    <span>Full-feature production</span>
                </div>

                <p>
                    Поточний напрям — покращення UX, пошуку
                    та AI/RAG-функцій, а також поступове
                    перенесення повної локальної функціональності
                    у вебверсію.
                </p>
            </article>
        </section>

        <section class="about-tip">
            <div>
                <p class="eyebrow">
                    RECOMMENDATION
                </p>

                <h2>
                    Як отримувати кращі результати
                </h2>
            </div>

            <p>
                Для точного факту використовуйте короткий конкретний запит.
                Для тематичного пошуку формулюйте думку природною мовою.
                Якщо потрібен баланс між точністю та змістом —
                починайте з Hybrid.
            </p>
        </section>
    </section>
</template>

<style scoped>
.about-page {
    padding: 64px 0 80px;
}

.about-hero {
    display: grid;
    grid-template-columns:
        minmax(0, 1.45fr)
        minmax(280px, 0.75fr);
    gap: 34px;
    align-items: stretch;
    margin-bottom: 58px;
}

.about-hero-copy {
    padding: 10px 0;
}

.about-hero h1 {
    margin-bottom: 18px;
}

.about-lead {
    max-width: 760px;
    margin: 0;
    color: var(--tekst-drugoryadnyi);
    font-size: 19px;
    line-height: 1.7;
}

.about-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
    margin-top: 24px;
    color: var(--tekst-drugoryadnyi);
    font-size: 14px;
}

.version-badge {
    display: inline-flex;
    align-items: center;
    min-height: 34px;
    padding: 0 12px;
    border: 1px solid var(--mezha);
    border-radius: 999px;
    background: var(--poverkhna-svitla);
    color: var(--morskyi-hlybokyi);
    font-weight: 700;
}

.about-purpose-card,
.about-card,
.workflow-step,
.search-mode-card,
.about-info-panel,
.about-tip {
    border: 1px solid var(--mezha);
    border-radius: 14px;
    background: var(--poverkhna-svitla);
}

.about-purpose-card {
    display: flex;
    flex-direction: column;
    justify-content: center;
    padding: 28px;
}

.about-purpose-label {
    margin-bottom: 14px;
    color: var(--blakytnyi-pryhlushenyi);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.14em;
}

.about-purpose-card strong {
    color: var(--morskyi-hlybokyi);
    font-size: 21px;
    line-height: 1.35;
}

.about-purpose-card p,
.about-card p,
.workflow-step p,
.search-mode-card p,
.about-info-panel p,
.about-tip > p,
.about-section-heading > p,
.deployment-note {
    color: var(--tekst-drugoryadnyi);
    line-height: 1.65;
}

.about-section {
    margin-bottom: 58px;
}

.about-section-heading {
    max-width: 760px;
    margin-bottom: 22px;
}

.about-section-heading h2,
.about-info-panel h2,
.about-tip h2 {
    margin: 6px 0 10px;
}

.about-section-heading > p {
    margin: 0;
}

.about-card-grid {
    display: grid;
    grid-template-columns:
        repeat(3, minmax(0, 1fr));
    gap: 16px;
}

.about-card,
.workflow-step,
.search-mode-card {
    padding: 22px;
}

.about-card h3,
.workflow-step h3,
.search-mode-card h3 {
    margin: 0 0 9px;
}

.about-card p,
.workflow-step p,
.search-mode-card p {
    margin: 0;
}

.workflow-grid {
    display: grid;
    grid-template-columns:
        repeat(4, minmax(0, 1fr));
    gap: 14px;
}

.workflow-number {
    display: inline-block;
    margin-bottom: 20px;
    color: var(--blakytnyi-pryhlushenyi);
    font-size: 24px;
    font-weight: 800;
}

.search-mode-grid {
    display: grid;
    grid-template-columns:
        repeat(3, minmax(0, 1fr));
    gap: 16px;
}

.search-mode-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    margin-bottom: 12px;
}

.search-mode-header h3 {
    margin: 0;
}

.search-mode-header span {
    padding: 5px 8px;
    border-radius: 999px;
    background: var(--poverkhna);
    color: var(--akvamarin-temnyi);
    font-size: 11px;
    font-weight: 700;
}

.deployment-note {
    margin: 16px 0 0;
    padding: 14px 16px;
    border-left:
        3px solid
        var(--blakytnyi-pryhlushenyi);
    background: var(--poverkhna);
    border-radius: 0 8px 8px 0;
    font-size: 14px;
}

.about-two-column {
    display: grid;
    grid-template-columns:
        repeat(2, minmax(0, 1fr));
    gap: 18px;
    margin-bottom: 58px;
}

.about-info-panel {
    padding: 26px;
}

.about-info-panel p:last-child {
    margin-bottom: 0;
}

.roadmap-line {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 9px;
    margin: 18px 0;
    color: var(--morskyi-hlybokyi);
    font-weight: 800;
}

.roadmap-line span:not(.roadmap-arrow) {
    padding: 7px 10px;
    border: 1px solid var(--mezha);
    border-radius: 7px;
    background: var(--poverkhna);
}

.roadmap-arrow {
    color: var(--blakytnyi-pryhlushenyi);
}

.about-tip {
    display: grid;
    grid-template-columns:
        minmax(230px, 0.75fr)
        minmax(0, 1.25fr);
    gap: 28px;
    align-items: center;
    padding: 28px;
}

.about-tip h2 {
    margin-bottom: 0;
}

.about-tip > p {
    margin: 0;
}

@media (max-width: 900px) {
    .about-hero,
    .about-two-column,
    .about-tip {
        grid-template-columns: 1fr;
    }

    .about-card-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }

    .workflow-grid,
    .search-mode-grid {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 620px) {
    .about-page {
        padding-top: 42px;
    }

    .about-card-grid,
    .workflow-grid,
    .search-mode-grid {
        grid-template-columns: 1fr;
    }

    .about-purpose-card,
    .about-card,
    .workflow-step,
    .search-mode-card,
    .about-info-panel,
    .about-tip {
        padding: 20px;
    }
}
</style>