const searchModeSelect = document.getElementById(
    "search-mode"
);

const searchModeHelp = document.getElementById(
    "search-mode-help"
);


const searchModeDescriptions = {
    lexical:
        "Lexical шукає точні збіги слів і фраз у текстах документів.",

    semantic:
        "Semantic шукає документи зі схожим змістом, навіть якщо слова запиту не збігаються буквально.",

    hybrid:
        "Hybrid поєднує пошук за словами та за змістом. Це основний рекомендований режим KnowledgeHub."
};


function updateSearchModeHelp() {
    if (
        !searchModeSelect
        || !searchModeHelp
    ) {
        return;
    }

    const selectedMode =
        searchModeSelect.value;

    searchModeHelp.textContent =
        searchModeDescriptions[
            selectedMode
        ] || "";
}


if (searchModeSelect) {
    searchModeSelect.addEventListener(
        "change",
        updateSearchModeHelp
    );

    updateSearchModeHelp();
}