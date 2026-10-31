<script setup>
defineProps({
    items: {
        type: Array,
        required: true
    }
})
</script>

<template>
    <nav
        class="breadcrumbs"
        aria-label="Breadcrumb"
    >
        <ol>
            <li
                v-for="(item, index) in items"
                :key="index"
            >
                <span
                    v-if="index > 0"
                    class="breadcrumb-separator"
                    aria-hidden="true"
                >
                    /
                </span>

                <RouterLink
                    v-if="item.to && !item.current"
                    class="breadcrumb-link"
                    :to="item.to"
                >
                    {{ item.label }}
                </RouterLink>

                <span
                    v-else
                    class="breadcrumb-current"
                    :aria-current="
                        item.current
                            ? 'page'
                            : undefined
                    "
                >
                    {{ item.label }}
                </span>
            </li>
        </ol>
    </nav>
</template>

<style scoped>
.breadcrumbs {
    margin-bottom: 22px;
}

.breadcrumbs ol {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
    margin: 0;
    padding: 0;
    list-style: none;
}

.breadcrumbs li {
    display: flex;
    align-items: center;
    gap: 8px;
    min-width: 0;
}

.breadcrumb-link {
    color: var(--akvamarin-temnyi);
    font-size: 14px;
    font-weight: 600;
    text-decoration: none;
}

.breadcrumb-link:hover {
    text-decoration: underline;
}

.breadcrumb-separator {
    color: var(--tekst-drugoryadnyi);
    opacity: 0.6;
}

.breadcrumb-current {
    max-width: 420px;
    overflow: hidden;
    color: var(--tekst-drugoryadnyi);
    font-size: 14px;
    font-weight: 600;
    text-overflow: ellipsis;
    white-space: nowrap;
}

@media (max-width: 620px) {
    .breadcrumb-current {
        max-width: 190px;
    }
}
</style>
