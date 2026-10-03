const editCollectionModal =
    document.getElementById(
        "edit-collection-modal"
    );

const deleteCollectionModal =
    document.getElementById(
        "delete-collection-modal"
    );


const openEditCollectionButton =
    document.getElementById(
        "open-edit-collection"
    );

const closeEditCollectionButton =
    document.getElementById(
        "close-edit-collection"
    );

const cancelEditCollectionButton =
    document.getElementById(
        "cancel-edit-collection"
    );


const openDeleteCollectionButton =
    document.getElementById(
        "open-delete-collection"
    );

const closeDeleteCollectionButton =
    document.getElementById(
        "close-delete-collection"
    );

const cancelDeleteCollectionButton =
    document.getElementById(
        "cancel-delete-collection"
    );


function openDialog(
    dialog
) {
    if (dialog) {
        dialog.showModal();
    }
}


function closeDialog(
    dialog
) {
    if (dialog) {
        dialog.close();
    }
}


if (openEditCollectionButton) {
    openEditCollectionButton.addEventListener(
        "click",
        () => openDialog(
            editCollectionModal
        )
    );
}


if (closeEditCollectionButton) {
    closeEditCollectionButton.addEventListener(
        "click",
        () => closeDialog(
            editCollectionModal
        )
    );
}


if (cancelEditCollectionButton) {
    cancelEditCollectionButton.addEventListener(
        "click",
        () => closeDialog(
            editCollectionModal
        )
    );
}


if (openDeleteCollectionButton) {
    openDeleteCollectionButton.addEventListener(
        "click",
        () => openDialog(
            deleteCollectionModal
        )
    );
}


if (closeDeleteCollectionButton) {
    closeDeleteCollectionButton.addEventListener(
        "click",
        () => closeDialog(
            deleteCollectionModal
        )
    );
}


if (cancelDeleteCollectionButton) {
    cancelDeleteCollectionButton.addEventListener(
        "click",
        () => closeDialog(
            deleteCollectionModal
        )
    );
}


for (
    const dialog
    of [
        editCollectionModal,
        deleteCollectionModal,
    ]
) {
    if (!dialog) {
        continue;
    }

    dialog.addEventListener(
        "click",
        (event) => {
            if (event.target === dialog) {
                dialog.close();
            }
        }
    );
}