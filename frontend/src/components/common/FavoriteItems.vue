<script setup>
import {
    onMounted,
    onUnmounted,
    ref,
    watch
} from "vue"

import {
    getFavoriteItems,
    removeFavorite
} from "../../utils/favoriteItems.js"

const props = defineProps({
    userId: {
        type: [
            Number,
            String
        ],
        required: true
    }
})

const items = ref([])

function refresh() {
    items.value =
        getFavoriteItems(
            props.userId
        )
}

function handleFavoritesChanged(
    event
) {
    if (
        String(
            event.detail?.userId
        )
        === String(
            props.userId
        )
    ) {
        refresh()
    }
}

function handleStorage(
    event
) {
    if (
        event.key?.startsWith(
            "knowledgehub.favoriteItems.v1."
        )
    ) {
        refresh()
    }
}

function removeItem(
    item
) {
    removeFavorite(
        props.userId,
        item
    )
}

watch(
    () => props.userId,
    refresh
)

onMounted(
    () => {
        refresh()

        window.addEventListener(
            "knowledgehub:favorites-changed",
            handleFavoritesChanged
        )

        window.addEventListener(
            "storage",
            handleStorage
        )
    }
)

onUnmounted(
    () => {
        window.removeEventListener(
            "knowledgehub:favorites-changed",
            handleFavoritesChanged
        )

        window.removeEventListener(
            "storage",
            handleStorage
        )
    }
)
</script>

<template>
    <section
        v-if="items.length"
        class="favorites-section"
    >
        <div class="favorites-heading">
            <div>
                <p class="eyebrow">
                    FAVORITES
                </p>

                <h2>
                    Обране
                </h2>

                <p>
                    Закріплені колекції
                    та документи.
                </p>
            </div>

            <span class="favorites-count">
                {{ items.length }}
            </span>
        </div>

        <div class="favorites-grid">
            <article
                v-for="item in items"
                :key="
                    item.type
                    + '-'
                    + item.collectionId
                    + '-'
                    + item.id
                "
                class="favorite-card"
            >
                <RouterLink
                    class="favorite-card-link"
                    :to="
                        item.type === 'document'
                            ? {
                                name: 'document',
                                params: {
                                    collectionId:
                                        item.collectionId,
                                    documentId:
                                        item.id
                                }
                            }
                            : {
                                name: 'collection-detail',
                                params: {
                                    collectionId:
                                        item.collectionId
                                }
                            }
                    "
                >
                    <span class="favorite-type">
                        {{
                            item.type === "document"
                                ? "ДОКУМЕНТ"
                                : "КОЛЕКЦІЯ"
                        }}
                    </span>

                    <strong>
                        {{ item.name }}
                    </strong>

                    <span
                        v-if="
                            item.type
                            === 'document'
                            && item.collectionName
                        "
                        class="favorite-context"
                    >
                        {{ item.collectionName }}
                    </span>

                    <span class="favorite-open">
                        Відкрити →
                    </span>
                </RouterLink>

                <button
                    class="favorite-remove"
                    type="button"
                    aria-label="Прибрати з обраного"
                    title="Прибрати з обраного"
                    @click="removeItem(item)"
                >
                    ×
                </button>
            </article>
        </div>
    </section>
</template>

<style scoped>
.favorites-section {
    margin-bottom: 32px;
    padding: 26px;

    border:
        1px solid
        var(--mezha);

    border-radius: 14px;

    background:
        var(--poverkhna-svitla);
}

.favorites-heading {
    display: flex;
    align-items: flex-end;
    justify-content: space-between;

    gap: 20px;

    margin-bottom: 18px;
}

.favorites-heading h2 {
    margin: 6px 0;
    font-size: 28px;
}

.favorites-heading p:last-child {
    margin: 0;

    color:
        var(--tekst-drugoryadnyi);
}

.favorites-count {
    display: inline-flex;

    min-width: 34px;
    height: 34px;

    align-items: center;
    justify-content: center;

    border:
        1px solid
        var(--mezha);

    border-radius: 999px;

    color:
        var(--akvamarin-temnyi);

    font-size: 13px;
    font-weight: 700;
}

.favorites-grid {
    display: grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(210px, 1fr)
        );

    gap: 14px;
}

.favorite-card {
    position: relative;

    min-width: 0;

    border:
        1px solid
        var(--mezha);

    border-radius: 10px;

    background:
        var(--fon-osnovnyi);
}

.favorite-card-link {
    display: flex;
    flex-direction: column;

    min-height: 128px;

    box-sizing: border-box;

    padding: 18px 44px 18px 18px;

    color:
        var(--tekst-osnovnyi);

    text-decoration: none;
}

.favorite-card-link:hover {
    background:
        var(--poverkhna);
}

.favorite-type {
    margin-bottom: 8px;

    color:
        var(--blakytnyi-pryhlushenyi);

    font-size: 11px;
    font-weight: 700;

    letter-spacing: 0.12em;
}

.favorite-card strong {
    overflow-wrap: anywhere;
}

.favorite-context {
    margin-top: 5px;

    color:
        var(--tekst-drugoryadnyi);

    font-size: 12px;
}

.favorite-open {
    margin-top: auto;
    padding-top: 14px;

    color:
        var(--akvamarin-temnyi);

    font-size: 13px;
    font-weight: 600;
}

.favorite-remove {
    position: absolute;

    top: 10px;
    right: 10px;

    width: 28px;
    height: 28px;

    padding: 0;

    border: 0;
    border-radius: 50%;

    background: transparent;

    color:
        var(--tekst-drugoryadnyi);

    font-size: 22px;
    line-height: 1;

    cursor: pointer;
}

.favorite-remove:hover {
    background:
        var(--poverkhna);

    color:
        var(--tekst-osnovnyi);
}

@media (max-width: 650px) {
    .favorites-heading {
        align-items: flex-start;
        flex-direction: column;
    }

    .favorites-grid {
        grid-template-columns: 1fr;
    }
}
</style>
