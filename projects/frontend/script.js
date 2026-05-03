(function () {
    "use strict";

    const STORAGE_KEY = "gaia_username";
    const MODEL_STORAGE_KEY = "gaia_care_provider";

    function getUsername() {
        return localStorage.getItem(STORAGE_KEY);
    }

    function main() {
        if (!getUsername()) {
            window.location.href = "login.html";
            return;
        }

        const chatEl = document.getElementById("chat");
        const headerEl = document.getElementById("app-header");
        const btnLogout = document.getElementById("btn-logout");
        const inputEl = document.getElementById("message-input");
        const fileInput = document.getElementById("file-input");
        const fileRow = document.getElementById("file-row");
        const fileChipName = document.getElementById("file-chip-name");
        const btnClearFile = document.getElementById("btn-clear-file");
        const btnSend = document.getElementById("btn-send");
        const btnAttach = document.getElementById("btn-attach");
        const modelSelect = document.getElementById("model-select");

        const username = getUsername();
        headerEl.textContent = `Hola, ${username} 👋`;

        btnLogout.addEventListener("click", () => {
            localStorage.removeItem(STORAGE_KEY);
            window.location.href = "login.html";
        });

        if (
            !chatEl ||
            !inputEl ||
            !fileInput ||
            !fileRow ||
            !fileChipName ||
            !btnClearFile ||
            !btnSend ||
            !btnAttach ||
            !modelSelect ||
            !btnLogout
        ) {
            console.error(
                "Gaia: faltan nodos en el HTML. ¿index.html desactualizado o caché antigua?"
            );
            return;
        }

        let selectedFile = null;

        function defaultBases() {
            if (
                typeof window.GAIA_API_BASES === "object" &&
                window.GAIA_API_BASES?.recognition &&
                window.GAIA_API_BASES?.care
            ) {
                return {
                    recognition: window.GAIA_API_BASES.recognition.replace(
                        /\/$/,
                        ""
                    ),
                    care: window.GAIA_API_BASES.care.replace(/\/$/, ""),
                    careRag: (
                        window.GAIA_API_BASES.careRag || "/api/c-rag"
                    ).replace(/\/$/, ""),
                };
            }
            return {
                recognition: "http://127.0.0.1:5000",
                care: "http://127.0.0.1:5002",
                careRag: "http://127.0.0.1:5001",
            };
        }

        function recBase() {
            return defaultBases().recognition;
        }

        function careBase() {
            return defaultBases().care;
        }

        function careRagBase() {
            return defaultBases().careRag;
        }

        function currentProvider() {
            return modelSelect.value === "rag" ? "rag" : "llm";
        }

        const THINKING_TEXT = [
            "Pensando…",
            "Consultando la base de datos…",
            "Buscando la mejor coincidencia…",
            "Procesando tu consulta…",
            "Casi listo…",
        ];

        const THINKING_IMAGE = [
            "Analizando la imagen…",
            "Preparando el modelo…",
            "Extrayendo características…",
            "Clasificando la planta…",
            "Un momento más…",
        ];

        /**
         * @param {boolean} forImage
         * @returns {{ stop: () => void }}
         */
        function startThinking(forImage) {
            const messages = forImage ? THINKING_IMAGE : THINKING_TEXT;
            const wrap = document.createElement("div");
            wrap.className = "msg msg-assistant msg-thinking-container";
            const bubble = document.createElement("div");
            bubble.className = "msg-bubble msg-thinking";
            const textEl = document.createElement("span");
            textEl.className = "msg-thinking-label";
            const dots = document.createElement("span");
            dots.className = "msg-thinking-dots";
            dots.setAttribute("aria-hidden", "true");
            for (let d = 0; d < 3; d++) {
                const dot = document.createElement("span");
                dot.className = "msg-thinking-dot";
                dot.textContent = ".";
                dots.appendChild(dot);
            }
            bubble.appendChild(textEl);
            bubble.appendChild(dots);
            wrap.appendChild(bubble);
            chatEl.appendChild(wrap);
            chatEl.scrollTop = chatEl.scrollHeight;

            let idx = 0;
            textEl.textContent = messages[idx];
            const intervalMs = 2400;
            const tick = window.setInterval(() => {
                idx = (idx + 1) % messages.length;
                textEl.textContent = messages[idx];
                chatEl.scrollTop = chatEl.scrollHeight;
            }, intervalMs);

            return {
                stop() {
                    window.clearInterval(tick);
                    wrap.remove();
                },
            };
        }

        const MIN_IMAGE_CONFIDENCE = 0.25;

        function presentCareAssistantResponse(care) {
            const { ok, data } = care;
            const llmText =
                typeof data?.response === "string" && data.response.trim();
            const human =
                typeof data?.humanized === "string" && data.humanized.trim();
            if (ok && llmText) {
                appendMessage("assistant", data.response.trim(), false, false);
            } else if (ok && human) {
                appendMessage("assistant", data.humanized.trim(), false, false);
            } else {
                appendMessage(
                    "assistant",
                    JSON.stringify(data, null, 2),
                    true,
                    !ok
                );
            }
        }

        function appendMessage(role, text, isRawJson = false, isError = false) {
            const wrap = document.createElement("div");
            wrap.className = `msg msg-${role}`;

            const bubble = document.createElement("div");
            bubble.className =
                "msg-bubble" +
                (isRawJson ? " raw" : "") +
                (isError ? " msg-error" : "");

            if (isRawJson) {
                const pre = document.createElement("pre");
                pre.textContent = text;
                bubble.appendChild(pre);
            } else {
                bubble.textContent = text;
            }

            wrap.appendChild(bubble);
            chatEl.appendChild(wrap);
            chatEl.scrollTop = chatEl.scrollHeight;
        }

        function showEmptyHint() {
            if (chatEl.querySelector(".empty-hint")) return;
            const p = document.createElement("p");
            p.className = "empty-hint";
            p.textContent = "Escribe texto o elige una imagen (no ambos).";
            chatEl.appendChild(p);
        }

        function removeEmptyHint() {
            chatEl.querySelector(".empty-hint")?.remove();
        }

        function updateInputMode() {
            const hasFile = Boolean(selectedFile);
            const hasText = inputEl.value.trim().length > 0;

            inputEl.disabled = hasFile;
            inputEl.placeholder = hasFile
                ? "Quita la imagen para escribir texto…"
                : "Texto sobre una planta (sin imagen)…";

            btnAttach.disabled = hasText;
            btnAttach.title = hasText
                ? "Borra el texto para usar imagen"
                : "Solo imagen (sin texto)";
        }

        function autoResize() {
            if (inputEl.disabled) return;
            inputEl.style.height = "auto";
            inputEl.style.height = `${Math.min(inputEl.scrollHeight, 128)}px`;
        }

        function setFile(file) {
            selectedFile = file;
            if (file) {
                inputEl.value = "";
                fileRow.hidden = false;
                fileChipName.textContent = file.name;
            } else {
                fileRow.hidden = true;
                fileChipName.textContent = "";
                fileInput.value = "";
            }
            updateInputMode();
            autoResize();
        }

        async function sendRecognition(file, base, username) {
            const fd = new FormData();
            fd.append("image", file);
            fd.append("username", username);
            const res = await fetch(`${base}/recognize`, {
                method: "POST",
                body: fd,
            });
            const text = await res.text();
            let data;
            try {
                data = JSON.parse(text);
            } catch {
                data = { _parseError: true, status: res.status, body: text };
            }
            return { ok: res.ok, status: res.status, data };
        }

        async function sendPlantCare(query, username) {
            const provider = currentProvider();
            let res;
            if (provider === "rag") {
                res = await fetch(`${careRagBase()}/plant`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ query, k: 3, username }),
                });
            } else {
                res = await fetch(`${careBase()}/generate`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        prompt:
                            "### Instruccion:\n" +
                            `Dame informacion sobre el cuidado de la planta o consulta: ${query}.\n\n` +
                            "### Respuesta:",
                        username,
                        max_new_tokens: 220,
                        temperature: 0.7,
                    }),
                });
            }
            const text = await res.text();
            let data;
            try {
                data = JSON.parse(text);
            } catch {
                data = { _parseError: true, status: res.status, body: text };
            }
            return { ok: res.ok, status: res.status, data };
        }

        async function onSend() {
            const text = inputEl.value.trim();

            if (selectedFile && text) {
                return;
            }
            if (!selectedFile && !text) return;

            removeEmptyHint();

            if (selectedFile) {
                appendMessage("user", `[imagen: ${selectedFile.name}]`);

                btnSend.disabled = true;
                let thinking = startThinking(true);
                try {
                    const { ok, data } = await sendRecognition(
                        selectedFile,
                        recBase(),
                        username
                    );
                    thinking.stop();

                    if (!ok) {
                        appendMessage(
                            "assistant",
                            JSON.stringify(data, null, 2),
                            true,
                            true
                        );
                    } else if (data.error) {
                        appendMessage(
                            "assistant",
                            String(data.error),
                            false,
                            true
                        );
                    } else {
                        const preds = data.predictions;
                        let bestProb = -1;
                        let bestPlant = "";
                        if (Array.isArray(preds)) {
                            for (const p of preds) {
                                const pr =
                                    p && p.probability != null
                                        ? Number(p.probability)
                                        : NaN;
                                if (Number.isFinite(pr) && pr > bestProb) {
                                    bestProb = pr;
                                    bestPlant =
                                        p.plant != null
                                            ? String(p.plant).trim()
                                            : "";
                                }
                            }
                        }

                        if (bestProb < MIN_IMAGE_CONFIDENCE || !bestPlant) {
                            appendMessage(
                                "assistant",
                                "No se reconoce la planta en la imagen con suficiente confianza (el resultado más alto está por debajo del 25%). Prueba con otra foto más clara, con buena luz y centrada en la planta.",
                                false,
                                false
                            );
                        } else {
                            thinking = startThinking(false);
                            const care = await sendPlantCare(
                                bestPlant,
                                username
                            );
                            thinking.stop();
                            presentCareAssistantResponse(care);
                        }
                    }
                } catch (e) {
                    thinking.stop();
                    appendMessage(
                        "assistant",
                        String(e.message || e),
                        true,
                        true
                    );
                } finally {
                    btnSend.disabled = false;
                    setFile(null);
                }
                return;
            }

            appendMessage("user", text);
            inputEl.value = "";
            autoResize();
            updateInputMode();
            btnSend.disabled = true;

            const thinking = startThinking(false);
            try {
                const { ok, status, data } = await sendPlantCare(
                    text,
                    username
                );
                thinking.stop();
                presentCareAssistantResponse({ ok, data });
            } catch (e) {
                thinking.stop();
                appendMessage("assistant", String(e.message || e), true, true);
            } finally {
                btnSend.disabled = false;
            }
        }

        btnSend.addEventListener("click", onSend);
        inputEl.addEventListener("keydown", (e) => {
            if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                onSend();
            }
        });
        inputEl.addEventListener("input", () => {
            if (inputEl.value.trim()) {
                setFile(null);
            }
            updateInputMode();
            autoResize();
        });

        btnAttach.addEventListener("click", () => {
            if (btnAttach.disabled) return;
            fileInput.click();
        });
        fileInput.addEventListener("change", () => {
            const f = fileInput.files?.[0];
            if (f) {
                setFile(f);
            }
        });

        btnClearFile.addEventListener("click", () => setFile(null));

        modelSelect.value =
            localStorage.getItem(MODEL_STORAGE_KEY) === "rag" ? "rag" : "llm";
        modelSelect.addEventListener("change", () => {
            localStorage.setItem(MODEL_STORAGE_KEY, currentProvider());
        });

        updateInputMode();
        showEmptyHint();
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", main);
    } else {
        main();
    }
})();
