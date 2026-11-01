import { readFileSync } from "node:fs"
import { fileURLToPath } from "node:url"

import { defineConfig } from "vite"
import vue from "@vitejs/plugin-vue"


const versionFile = fileURLToPath(
    new URL(
        "../VERSION",
        import.meta.url
    )
)

const appVersion = readFileSync(
    versionFile,
    "utf8"
).trim()


export default defineConfig({
    plugins: [
        vue()
    ],

    define: {
        __APP_VERSION__: JSON.stringify(
            appVersion
        )
    },

    server: {
        host: "127.0.0.1",
        port: 5173,
        strictPort: true,

        proxy: {
            "/api": {
                target: "http://127.0.0.1:8000",
                changeOrigin: false
            }
        }
    }
})
