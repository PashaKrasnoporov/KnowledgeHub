import {
    createApp
} from "vue"

import App from "./App.vue"
import router from "./router/index.js"

import "./styles/jinja/baza.css"
import "./styles/jinja/main.css"
import "./styles/jinja/komponenty/formy.css"
import "./styles/jinja/komponenty/povidomlennia.css"
import "./styles/jinja/komponenty/file_picker.css"
import "./styles/jinja/storinky/reiestratsiia.css"
import "./styles/jinja/storinky/collections.css"
import "./styles/jinja/storinky/search.css"
import "./styles/jinja/storinky/document_links.css"
import "./styles/jinja/storinky/collection_manage.css"
import "./styles/jinja/storinky/document_view.css"
import "./styles/jinja/storinky/document_manage.css"
import "./styles/jinja/storinky/admin.css"
import "./styles/jinja/storinky/errors.css"
import "./styles/jinja/responsive.css"

import "./styles/research.css"
import "./styles/claim_grounding.css"
import "./styles/research_ux.css"

createApp(
    App
)
    .use(
        router
    )
    .mount(
        "#app"
    )
