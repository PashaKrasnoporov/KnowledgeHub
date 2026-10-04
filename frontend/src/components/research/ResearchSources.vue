<script setup>
defineProps({
    collectionId: {
        type: Number,
        required: true
    },

    sources: {
        type: Array,
        default: () => []
    }
})
</script>

<template>
    <div class="research-sources">
        <div class="research-result-heading">
            <h3>
                Джерела
            </h3>

            <span>
                {{ sources.length }} фрагм.
            </span>
        </div>

        <article
            v-for="source in sources"
            :id="
                `research-source-${source.source_number}`
            "
            :key="
                `${source.document_id}-${source.chunk_index}`
            "
            class="research-source-card"
        >
            <div class="research-source-number">
                {{ source.source_number }}
            </div>

            <div class="research-source-content">
                <div class="research-source-meta">
                    <RouterLink
                        :to="{
                            name: 'document',
                            params: {
                                collectionId,
                                documentId:
                                    source.document_id
                            }
                        }"
                    >
                        {{ source.original_name }}
                    </RouterLink>

                    <span>
                        chunk {{ source.chunk_index }}
                    </span>
                </div>

                <p>
                    {{ source.excerpt }}
                </p>

                <div class="research-score-row">
                    <span>
                        Hybrid:
                        <strong>
                            {{
                                Number(
                                    source.score
                                ).toFixed(3)
                            }}
                        </strong>
                    </span>

                    <span>
                        Semantic:
                        <strong>
                            {{
                                Number(
                                    source.semantic_score
                                ).toFixed(3)
                            }}
                        </strong>
                    </span>

                    <span>
                        Lexical:
                        <strong>
                            {{
                                Number(
                                    source.lexical_score
                                ).toFixed(3)
                            }}
                        </strong>
                    </span>
                </div>
            </div>
        </article>
    </div>
</template>
