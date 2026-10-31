const PREFIX =
    "knowledgehub.favoriteItems.v1"

function storageKey(
    userId
) {
    return (
        PREFIX
        + "."
        + String(userId)
    )
}

function notify(
    userId
) {
    window.dispatchEvent(
        new CustomEvent(
            "knowledgehub:favorites-changed",
            {
                detail: {
                    userId:
                        String(userId)
                }
            }
        )
    )
}

export function getFavoriteItems(
    userId
) {
    if (!userId) {
        return []
    }

    try {
        const value =
            JSON.parse(
                localStorage.getItem(
                    storageKey(userId)
                )
                || "[]"
            )

        return Array.isArray(value)
            ? value
            : []
    }
    catch {
        return []
    }
}

function saveFavoriteItems(
    userId,
    items
) {
    localStorage.setItem(
        storageKey(userId),
        JSON.stringify(items)
    )

    notify(userId)
}

function sameItem(
    a,
    b
) {
    return (
        a.type === b.type
        && String(a.id)
            === String(b.id)
        && String(
            a.collectionId
        ) === String(
            b.collectionId
        )
    )
}

export function isFavorite(
    userId,
    item
) {
    return getFavoriteItems(
        userId
    ).some(
        existing =>
            sameItem(
                existing,
                item
            )
    )
}

export function toggleFavorite(
    userId,
    item
) {
    if (
        !userId
        || !item?.id
        || !item?.type
    ) {
        return false
    }

    const items =
        getFavoriteItems(
            userId
        )

    const exists =
        items.some(
            existing =>
                sameItem(
                    existing,
                    item
                )
        )

    if (exists) {
        saveFavoriteItems(
            userId,
            items.filter(
                existing =>
                    !sameItem(
                        existing,
                        item
                    )
            )
        )

        return false
    }

    saveFavoriteItems(
        userId,
        [
            {
                ...item,
                savedAt:
                    new Date()
                        .toISOString()
            },
            ...items
        ]
    )

    return true
}

export function removeFavorite(
    userId,
    item
) {
    const items =
        getFavoriteItems(
            userId
        ).filter(
            existing =>
                !sameItem(
                    existing,
                    item
                )
        )

    saveFavoriteItems(
        userId,
        items
    )
}
