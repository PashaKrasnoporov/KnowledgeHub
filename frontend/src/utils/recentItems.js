const PREFIX = "knowledgehub.recentItems.v2"
const LEGACY_KEY = "knowledgehub.recentItems.v1"
const MAX_ITEMS = 6


function storageKey(userId) {
    return `${PREFIX}.${String(userId)}`
}


function discardLegacyStorage() {
    localStorage.removeItem(
        LEGACY_KEY
    )
}


function notify(userId) {
    window.dispatchEvent(
        new CustomEvent(
            "knowledgehub:recent-changed",
            {
                detail: {
                    userId: String(userId)
                }
            }
        )
    )
}


function readItems(userId) {
    if (!userId) {
        return []
    }

    discardLegacyStorage()

    try {
        const value = JSON.parse(
            localStorage.getItem(
                storageKey(userId)
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


function saveItems(userId, items) {
    if (!userId) {
        return
    }

    localStorage.setItem(
        storageKey(userId),
        JSON.stringify(
            items.slice(0, MAX_ITEMS)
        )
    )

    notify(userId)
}


function sameItem(a, b) {
    return (
        a.type === b.type
        && String(a.id) === String(b.id)
        && String(a.collectionId) === String(b.collectionId)
    )
}


function addItem(userId, item) {
    const items = readItems(userId).filter(
        existing => !sameItem(existing, item)
    )

    saveItems(
        userId,
        [
            {
                ...item,
                visitedAt: new Date().toISOString()
            },
            ...items
        ]
    )
}


export function addRecentCollection(userId, collection) {
    if (!userId || !collection?.id) {
        return
    }

    addItem(
        userId,
        {
            type: "collection",
            id: collection.id,
            collectionId: collection.id,
            name: collection.name || "Колекція"
        }
    )
}


export function addRecentDocument(userId, collectionId, document) {
    if (!userId || !collectionId || !document?.id) {
        return
    }

    addItem(
        userId,
        {
            type: "document",
            id: document.id,
            collectionId: Number(collectionId),
            name: document.original_name || "Документ"
        }
    )
}


export function getRecentItems(userId) {
    return readItems(userId)
}


export function updateRecentCollection(userId, collection) {
    if (!userId || !collection?.id) {
        return
    }

    const collectionId = Number(collection.id)

    const items = readItems(userId).map(
        item => {
            if (Number(item.collectionId) !== collectionId) {
                return item
            }

            if (item.type === "collection") {
                return {
                    ...item,
                    name: collection.name
                }
            }

            return item
        }
    )

    saveItems(userId, items)
}


export function removeRecentCollection(userId, collectionId) {
    const normalized = Number(collectionId)

    const items = readItems(userId).filter(
        item => Number(item.collectionId) !== normalized
    )

    saveItems(userId, items)
}


export function removeRecentDocument(userId, collectionId, documentId) {
    const items = readItems(userId).filter(
        item => !(
            item.type === "document"
            && Number(item.collectionId) === Number(collectionId)
            && Number(item.id) === Number(documentId)
        )
    )

    saveItems(userId, items)
}
