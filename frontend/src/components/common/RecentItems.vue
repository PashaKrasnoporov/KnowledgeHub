<script setup>
import {
    onMounted,
    ref
} from "vue"

import {
    getRecentItems
} from "../../utils/recentItems.js"

const items = ref([])

onMounted(
    () => {
        items.value = getRecentItems()
    }
)
</script>

<template>
    <section
        v-if="items.length"
        class="recent-section"
    >
        <div class="recent-heading">
            <div>
                <p class="eyebrow">
                    RECENT
                </p>

                <h2>
                    Нещодавні
                </h2>

                <p>
                    Швидкий доступ до останніх
                    відкритих матеріалів.
                </p>
            </div>

            <RouterLink
                class="recent-all-link"
                :to="{ name: 'collections' }"
            >
                Усі колекції →
            </RouterLink>
        </div>

        <div class="recent-grid">
            <RouterLink
                v-for="item in items"
                :key="
                    item.type
                    + '-'
                    + item.collectionId
                    + '-'
                    + item.id
                "
                class="recent-card"
                :to="
                    item.type === 'document'
                        ? {
                            name: 'document',
                            params: {
                                collectionId: item.collectionId,
                                documentId: item.id
                            }
                        }
                        : {
                            name: 'collection-detail',
                            params: {
                                collectionId: item.collectionId
                            }
                        }
                "
            >
                <span class="recent-type">
                    {{
                        item.type === "document"
                            ? "ДОКУМЕНТ"
                            : "КОЛЕКЦІЯ"
                    }}
                </span>

                <strong>
                    {{ item.name }}
                </strong>

                <span class="recent-open">
                    Відкрити →
                </span>
            </RouterLink>
        </div>
    </section>
</template>

<style scoped>
.recent-section {
    margin-bottom: 44px;
    padding: 26px;
    background: var(--poverkhna-svitla);
    border: 1px solid var(--mezha);
    border-radius: 14px;
}

.recent-heading {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    gap: 24px;
    margin-bottom: 20px;
}

.recent-heading h2 {
    margin: 6px 0;
    font-size: 28px;
}

.recent-heading p:last-child {
    margin: 0;
    color: var(--tekst-drugoryadnyi);
}

.recent-all-link,
.recent-open {
    color: var(--akvamarin-temnyi);
    font-weight: 600;
    text-decoration: none;
}

.recent-grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(210px, 1fr));
    gap: 14px;
}

.recent-card {
    display: flex;
    min-height: 120px;
    padding: 18px;
    box-sizing: border-box;
    flex-direction: column;
    gap: 8px;

    background: var(--fon-osnovnyi);
    border: 1px solid var(--mezha);
    border-radius: 10px;

    color: var(--tekst-osnovnyi);
    text-decoration: none;

    transition:
        transform 0.15s ease,
        border-color 0.15s ease,
        box-shadow 0.15s ease;
}

.recent-card:hover {
    transform: translateY(-2px);
    border-color: var(--mezha-temna);
    box-shadow:
        0 6px 18px
        rgba(38, 60, 67, 0.06);
}

.recent-type {
    color: var(--blakytnyi-pryhlushenyi);
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.12em;
}

.recent-card strong {
    flex: 1;
    overflow-wrap: anywhere;
}

.recent-open {
    font-size: 13px;
}

@media (max-width: 650px) {
    .recent-heading {
        align-items: flex-start;
        flex-direction: column;
    }

    .recent-grid {
        grid-template-columns: 1fr;
    }
}
</style>
