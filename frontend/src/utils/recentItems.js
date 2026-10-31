const STORAGE_KEY =
    "knowledgehub.recentItems.v1"

const MAX_ITEMS = 6


function readItems() {
    try {
        const value =
            JSON.parse(
                localStorage.getItem(
                    STORAGE_KEY
                ) || "[]"
            )

        return Array.isArray(value)
            ? value
            : []
    }
    catch {
        return []
    }
}


function saveItems(
    items
) {
    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(
            items.slice(
                0,
                MAX_ITEMS
            )
        )
    )
}


function addItem(
    item
) {
    const items =
        readItems()

    const filtered =
        items.filter(
            existing =>
                !(
                    existing.type === item.type
                    && existing.id === item.id
                    && existing.collectionId
                        === item.collectionId
                )
        )

    saveItems([
        {
            ...item,
            visitedAt:
                new Date().toISOString()
        },
        ...filtered
    ])
}


export function addRecentCollection(
    collection
) {
    if (!collection?.id) {
        return
    }

    addItem({
        type: "collection",
        id: collection.id,
        collectionId:
            collection.id,
        name:
            collection.name
            || "Колекція"
    })
}


export function addRecentDocument(
    collectionId,
    document
) {
    if (
        !collectionId
        || !document?.id
    ) {
        return
    }

    addItem({
        type: "document",
        id: document.id,
        collectionId:
            Number(collectionId),
        name:
            document.original_name
            || "Документ"
    })
}


export function getRecentItems() {
    return readItems()
}


export function clearRecentItems() {
    localStorage.removeItem(
        STORAGE_KEY
    )
}
