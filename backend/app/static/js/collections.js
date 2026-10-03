const collectionsPage = document.querySelector(
    ".collections-page"
);

const modal = document.getElementById(
    "collection-modal"
);

const openButton = document.getElementById(
    "open-collection-modal"
);

const emptyOpenButton = document.getElementById(
    "open-collection-modal-empty"
);

const closeButton = document.getElementById(
    "close-collection-modal"
);

const cancelButton = document.getElementById(
    "cancel-collection-modal"
);

const nameInput = document.getElementById(
    "collection-name"
);


function openModal() {
    if (!modal) {
        return;
    }

    modal.showModal();

    if (nameInput) {
        nameInput.focus();
    }
}


function closeModal() {
    if (!modal) {
        return;
    }

    modal.close();
}


if (openButton) {
    openButton.addEventListener(
        "click",
        openModal
    );
}


if (emptyOpenButton) {
    emptyOpenButton.addEventListener(
        "click",
        openModal
    );
}


if (closeButton) {
    closeButton.addEventListener(
        "click",
        closeModal
    );
}


if (cancelButton) {
    cancelButton.addEventListener(
        "click",
        closeModal
    );
}


if (modal) {
    modal.addEventListener(
        "click",
        (event) => {
            if (event.target === modal) {
                closeModal();
            }
        }
    );
}


if (
    collectionsPage
    && collectionsPage.dataset.openCreateModal
        === "true"
) {
    openModal();
}