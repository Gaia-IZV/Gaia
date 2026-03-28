(function () {
   "use strict";

   function main() {
      const chatEl = document.getElementById("chat");
      const inputEl = document.getElementById("message-input");
      const fileInput = document.getElementById("file-input");
      const fileRow = document.getElementById("file-row");
      const fileChipName = document.getElementById("file-chip-name");
      const btnClearFile = document.getElementById("btn-clear-file");
      const btnSend = document.getElementById("btn-send");
      const btnAttach = document.getElementById("btn-attach");

      if (
         !chatEl ||
         !inputEl ||
         !fileInput ||
         !fileRow ||
         !fileChipName ||
         !btnClearFile ||
         !btnSend ||
         !btnAttach
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
            };
         }
         return {
            recognition: "http://127.0.0.1:5000",
            care: "http://127.0.0.1:5001",
         };
      }

      function recBase() {
         return defaultBases().recognition;
      }

      function careBase() {
         return defaultBases().care;
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

      async function sendRecognition(file, base) {
         const fd = new FormData();
         fd.append("image", file);
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

      async function sendPlantCare(query, base) {
         const res = await fetch(`${base}/plant`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query, k: 3 }),
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
            const thinking = startThinking(true);
            try {
               const { ok, status, data } = await sendRecognition(
                  selectedFile,
                  recBase()
               );
               thinking.stop();
               const raw = JSON.stringify(data, null, 2);
               appendMessage("assistant", raw, true, !ok);
            } catch (e) {
               thinking.stop();
               appendMessage("assistant", String(e.message || e), true, true);
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
            const { ok, status, data } = await sendPlantCare(text, careBase());
            thinking.stop();
            const raw = JSON.stringify(data, null, 2);
            appendMessage("assistant", raw, true, !ok);
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

      updateInputMode();
      showEmptyHint();
   }

   if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", main);
   } else {
      main();
   }
})();
