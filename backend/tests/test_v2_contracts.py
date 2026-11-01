from pathlib import Path


PROJECT_ROOT = (
    Path(__file__)
    .resolve()
    .parents[2]
)


def read(relative: str) -> str:
    return (
        PROJECT_ROOT
        / relative
    ).read_text(
        encoding="utf-8-sig"
    )


def flat(relative: str) -> str:
    return " ".join(
        read(relative).split()
    )


def require(
    source: str,
    marker: str,
    label: str,
) -> None:
    assert marker in source, (
        f"Missing contract: {label}"
    )


def forbid(
    source: str,
    marker: str,
    label: str,
) -> None:
    assert marker not in source, (
        f"Forbidden contract found: {label}"
    )


def main() -> None:

    # -----------------------------------------------------
    # Version
    # -----------------------------------------------------

    version = (
        PROJECT_ROOT
        / "VERSION"
    ).read_text(
        encoding="utf-8"
    ).strip()

    assert version.startswith(
        "2.0.0"
    ), (
        "Unexpected VERSION: "
        + version
    )

    # -----------------------------------------------------
    # Per-user Recent
    # -----------------------------------------------------

    recent = read(
        "frontend/src/utils/recentItems.js"
    )

    require(
        recent,
        "knowledgehub.recentItems.v2",
        "Recent storage V2",
    )

    require(
        recent,
        "userId",
        "Recent per-user scope",
    )

    require(
        recent,
        "removeRecentCollection",
        "Recent collection cleanup",
    )

    require(
        recent,
        "removeRecentDocument",
        "Recent document cleanup",
    )

    # -----------------------------------------------------
    # Favorites consistency
    # -----------------------------------------------------

    favorites = read(
        "frontend/src/utils/favoriteItems.js"
    )

    require(
        favorites,
        "updateFavoriteCollection",
        "Favorite rename synchronization",
    )

    require(
        favorites,
        "removeFavoriteCollection",
        "Favorite collection cleanup",
    )

    require(
        favorites,
        "removeFavoriteDocument",
        "Favorite document cleanup",
    )

    # -----------------------------------------------------
    # Collection page / query privacy
    # -----------------------------------------------------

    collection = flat(
        "frontend/src/views/CollectionDetailView.vue"
    )

    forbid(
        collection,
        'localStorage.getItem( "knowledgehub.searchQuery"',
        "Persisted search query read",
    )

    forbid(
        collection,
        'localStorage.setItem( "knowledgehub.searchQuery"',
        "Persisted search query write",
    )

    require(
        collection,
        'localStorage.removeItem( "knowledgehub.searchQuery"',
        "Legacy search-query cleanup",
    )

    require(
        collection,
        "collection-workspace-tabs",
        "Collection workspace tabs",
    )

    require(
        collection,
        "startProcessingPolling",
        "Document processing polling",
    )

    # -----------------------------------------------------
    # Research question privacy
    # -----------------------------------------------------

    research = flat(
        "frontend/src/components/research/ResearchPanel.vue"
    )

    forbid(
        research,
        'localStorage.getItem( "knowledgehub.researchQuestion"',
        "Persisted research question read",
    )

    forbid(
        research,
        'localStorage.setItem( "knowledgehub.researchQuestion"',
        "Persisted research question write",
    )

    require(
        research,
        'localStorage.removeItem( "knowledgehub.researchQuestion"',
        "Legacy research-question cleanup",
    )

    # -----------------------------------------------------
    # Session expiry
    # -----------------------------------------------------

    client = read(
        "frontend/src/api/client.js"
    )

    require(
        client,
        "knowledgehub:auth-expired",
        "Session expiry event",
    )

    app = read(
        "frontend/src/App.vue"
    )

    require(
        app,
        "handleAuthExpired",
        "Central auth-expiry handler",
    )

    # -----------------------------------------------------
    # Processing lifecycle
    # -----------------------------------------------------

    pipeline = read(
        "backend/app/services/document_pipeline_service.py"
    )

    require(
        pipeline,
        "processing_status",
        "Processing lifecycle",
    )

    require(
        pipeline,
        '"processing"',
        "Processing intermediate status",
    )

    require(
        pipeline,
        '"ready"',
        "Processing ready status",
    )

    require(
        pipeline,
        '"error"',
        "Processing error status",
    )

    # -----------------------------------------------------
    # Search snippets
    # -----------------------------------------------------

    search_schema = read(
        "backend/app/schemas/search.py"
    )

    require(
        search_schema,
        "snippet: str | None",
        "Search result snippet field",
    )

    semantic = read(
        "backend/app/services/semantic_search_service.py"
    )

    require(
        semantic,
        "document_snippets",
        "Semantic matched chunk snippets",
    )

    hybrid = read(
        "backend/app/services/hybrid_search_service.py"
    )

    require(
        hybrid,
        "semantic_snippets",
        "Hybrid matched chunk snippets",
    )

    # -----------------------------------------------------
    # RAG UX
    # -----------------------------------------------------

    answer = read(
        "frontend/src/components/research/ResearchAnswer.vue"
    )

    require(
        answer,
        "research-advanced-details",
        "Collapsed RAG diagnostics",
    )

    # -----------------------------------------------------
    # Account/Admin UX
    # -----------------------------------------------------

    registration = read(
        "frontend/src/views/RegisterView.vue"
    )

    require(
        registration,
        "Увійти в систему",
        "Registration login flow",
    )

    profile = read(
        "frontend/src/views/ProfileView.vue"
    )

    require(
        profile,
        "profile-details",
        "Profile V2",
    )

    admin = read(
        "frontend/src/views/AdminView.vue"
    )

    require(
        admin,
        "admin-confirm-dialog",
        "Admin confirmation dialog",
    )

    # -----------------------------------------------------
    # Single version source
    # -----------------------------------------------------

    vite = read(
        "frontend/vite.config.js"
    )

    require(
        vite,
        "__APP_VERSION__",
        "Frontend version injection",
    )

    backend_version = read(
        "backend/app/version.py"
    )

    require(
        backend_version,
        "APP_VERSION",
        "Backend version source",
    )

    print(
        "KnowledgeHub V2 contract tests: PASS"
    )


if __name__ == "__main__":
    main()