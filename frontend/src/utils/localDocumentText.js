import * as pdfjsLib from "pdfjs-dist"

import pdfWorkerUrl from
    "pdfjs-dist/build/pdf.worker.min.mjs?url"

import mammoth from
    "mammoth/mammoth.browser"


pdfjsLib.GlobalWorkerOptions.workerSrc =
    pdfWorkerUrl


function getExtension(
    fileName
) {
    const dotIndex =
        fileName.lastIndexOf(".")

    if (dotIndex === -1) {
        return ""
    }

    return fileName
        .slice(dotIndex)
        .toLowerCase()
}


async function extractTxtText(
    file
) {
    return file.text()
}


async function extractPdfText(
    file
) {
    const arrayBuffer =
        await file.arrayBuffer()

    const loadingTask =
        pdfjsLib.getDocument({
            data:
                new Uint8Array(
                    arrayBuffer
                )
        })

    const pdf =
        await loadingTask.promise

    const pages = []

    try {
        for (
            let pageNumber = 1;
            pageNumber <= pdf.numPages;
            pageNumber += 1
        ) {
            const page =
                await pdf.getPage(
                    pageNumber
                )

            const textContent =
                await page.getTextContent()

            const pageText =
                textContent.items
                    .map(
                        item =>
                            "str" in item
                                ? item.str
                                : ""
                    )
                    .join(" ")

            pages.push(
                pageText
            )

            page.cleanup()
        }
    }
    finally {
        await pdf.destroy()
    }

    return pages.join("\n\n")
}


async function extractDocxText(
    file
) {
    const arrayBuffer =
        await file.arrayBuffer()

    const result =
        await mammoth.extractRawText({
            arrayBuffer
        })

    return result.value
}


export async function extractLocalDocumentText(
    file
) {
    const extension =
        getExtension(
            file.name
        )

    if (extension === ".txt") {
        return {
            type: "TXT",
            text:
                await extractTxtText(
                    file
                )
        }
    }

    if (extension === ".pdf") {
        return {
            type: "PDF",
            text:
                await extractPdfText(
                    file
                )
        }
    }

    if (extension === ".docx") {
        return {
            type: "DOCX",
            text:
                await extractDocxText(
                    file
                )
        }
    }

    throw new Error(
        "UNSUPPORTED_FILE_TYPE"
    )
}