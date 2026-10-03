const uploadModal = document.getElementById(
    "upload-modal"
);

const openUploadButton = document.getElementById(
    "open-upload-modal"
);

const closeUploadButton = document.getElementById(
    "close-upload-modal"
);

const cancelUploadButton = document.getElementById(
    "cancel-upload-modal"
);

const documentFileInput = document.getElementById(
    "document-file"
);


function openUploadModal() {
    if (!uploadModal) {
        return;
    }

    uploadModal.showModal();

    if (documentFileInput) {
        documentFileInput.focus();
    }
}


function closeUploadModal() {
    if (!uploadModal) {
        return;
    }

    uploadModal.close();
}


if (openUploadButton) {
    openUploadButton.addEventListener(
        "click",
        openUploadModal
    );
}


if (closeUploadButton) {
    closeUploadButton.addEventListener(
        "click",
        closeUploadModal
    );
}


if (cancelUploadButton) {
    cancelUploadButton.addEventListener(
        "click",
        closeUploadModal
    );
}


if (uploadModal) {
    uploadModal.addEventListener(
        "click",
        (event) => {
            if (event.target === uploadModal) {
                closeUploadModal();
            }
        }
    );
}