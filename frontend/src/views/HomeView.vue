<template>
    <section class="hero">
        <div class="hero-content">
            <p class="eyebrow">
                PERSONAL KNOWLEDGE PLATFORM
            </p>

            <h1>
                Організовуйте свої знання в одному місці
            </h1>

            <p class="hero-description">
                KnowledgeHub — платформа для створення колекцій,
                зберігання документів, пошуку інформації та
                подальшого інтелектуального аналізу матеріалів.
            </p>

            <div class="hero-actions">
                <RouterLink
                    class="button primary"
                    :to="{ name: 'about' }"
                >
                    Дізнатися більше
                </RouterLink>
            </div>
        </div>
    </section>

    <section class="features">
        <article class="feature-card">
            <h2>Колекції</h2>

            <p>
                Об'єднуйте документи за темами,
                проєктами або напрямами дослідження.
            </p>
        </article>

        <article class="feature-card">
            <h2>Документи</h2>

            <p>
                Зберігайте власну структуровану
                базу матеріалів.
            </p>
        </article>

        <article class="feature-card">
            <h2>Пошук</h2>

            <p>
                Швидко знаходьте необхідну інформацію
                серед своїх матеріалів.
            </p>
        </article>
    </section>
</template>
