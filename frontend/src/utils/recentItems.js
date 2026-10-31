const STORAGE_KEY = "knowledgehub.recentItems.v1"
const MAX_ITEMS = 6

function readItems() {
    try {
        const value = JSON.parse(
            localStorage.getItem(STORAGE_KEY) || "[]"
        )

        return Array.isArray(value)
            ? value
            : []
    }
    catch {
        return []
    }
}

function saveItems(items) {
    localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify(
            items.slice(0, MAX_ITEMS)
        )
    )
}

function addItem(item) {
    const items = readItems().filter(
        existing =>
            !(
                existing.type === item.type
                && existing.id === item.id
                && existing.collectionId === item.collectionId
            )
    )

    saveItems([
        {
            ...item,
            visitedAt: new Date().toISOString()
        },
        ...items
    ])
}

export function addRecentCollection(collection) {
    if (!collection?.id) {
        return
    }

    addItem({
        type: "collection",
        id: collection.id,
        collectionId: collection.id,
        name: collection.name || "\u041a\u043e\u043b\u0435\u043a\u0446\u0456\u044f"
    })
}

export function addRecentDocument(
    collectionId,
    document
) {
    if (!collectionId || !document?.id) {
        return
    }

    addItem({
        type: "document",
        id: document.id,
        collectionId: Number(collectionId),
        name:
            document.original_name
            || "\u0414\u043e\u043a\u0443\u043c\u0435\u043d\u0442"
    })
}

export function getRecentItems() {
    return readItems()
}
