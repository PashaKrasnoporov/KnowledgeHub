const deleteDocumentModal =
    document.getElementById(
        "delete-document-modal"
    );

const openDeleteDocumentButton =
    document.getElementById(
        "open-delete-document"
    );

const closeDeleteDocumentButton =
    document.getElementById(
        "close-delete-document"
    );

const cancelDeleteDocumentButton =
    document.getElementById(
        "cancel-delete-document"
    );


function openDeleteDocumentModal() {
    if (deleteDocumentModal) {
        deleteDocumentModal.showModal();
    }
}


function closeDeleteDocumentModal() {
    if (deleteDocumentModal) {
        deleteDocumentModal.close();
    }
}


if (openDeleteDocumentButton) {
    openDeleteDocumentButton.addEventListener(
        "click",
        openDeleteDocumentModal
    );
}


if (closeDeleteDocumentButton) {
    closeDeleteDocumentButton.addEventListener(
        "click",
        closeDeleteDocumentModal
    );
}


if (cancelDeleteDocumentButton) {
    cancelDeleteDocumentButton.addEventListener(
        "click",
        closeDeleteDocumentModal
    );
}


if (deleteDocumentModal) {
    deleteDocumentModal.addEventListener(
        "click",
        (event) => {
            if (
                event.target
                === deleteDocumentModal
            ) {
                closeDeleteDocumentModal();
            }
        }
    );
}