const STORAGE_KEYS = {
   recognition: "gaia_api_recognition",
   care: "gaia_api_care",
};

const chatEl = document.getElementById("chat");
const inputEl = document.getElementById("message-input");
const fileInput = document.getElementById("file-input");
const fileChip = document.getElementById("file-chip");
const btnSend = document.getElementById("btn-send");
const btnAttach = document.getElementById("btn-attach");
const btnSettings = document.getElementById("btn-settings");
const settingsPanel = document.getElementById("settings-panel");
const urlRecognition = document.getElementById("url-recognition");
const urlCare = document.getElementById("url-care");

let selectedFile = null;

function defaultBases() {
   if (
      typeof window.GAIA_API_BASES === "object" &&
      window.GAIA_API_BASES?.recognition &&
      window.GAIA_API_BASES?.care
   ) {
      return {
         recognition: window.GAIA_API_BASES.recognition,
         care: window.GAIA_API_BASES.care,
      };
   }
   return {
      recognition: "http://127.0.0.1:5000",
      care: "http://127.0.0.1:5001",
   };
}

function loadUrls() {
   const d = defaultBases();
   urlRecognition.value =
      localStorage.getItem(STORAGE_KEYS.recognition) || d.recognition;
   urlCare.value = localStorage.getItem(STORAGE_KEYS.care) || d.care;
}

function saveUrls() {
   localStorage.setItem(
      STORAGE_KEYS.recognition,
      urlRecognition.value.replace(/\/$/, "")
   );
   localStorage.setItem(STORAGE_KEYS.care, urlCare.value.replace(/\/$/, ""));
}

function baseUrl(input) {
   return input.value.replace(/\/$/, "");
}

function appendMessage(role, label, text, isRawJson = false, isError = false) {
   const wrap = document.createElement("div");
   wrap.className = `msg msg-${role}`;

   const meta = document.createElement("div");
   meta.className = "msg-meta";
   meta.textContent = label;

   const bubble = document.createElement("div");
   bubble.className =
      "msg-bubble" + (isRawJson ? " raw" : "") + (isError ? " msg-error" : "");

   if (isRawJson) {
      const pre = document.createElement("pre");
      pre.textContent = text;
      bubble.appendChild(pre);
   } else {
      bubble.textContent = text;
   }

   wrap.appendChild(meta);
   wrap.appendChild(bubble);
   chatEl.appendChild(wrap);
   chatEl.scrollTop = chatEl.scrollHeight;
}

function showEmptyHint() {
   if (chatEl.querySelector(".empty-hint")) return;
   const p = document.createElement("p");
   p.className = "empty-hint";
   p.textContent =
      "Envía texto o una imagen para ver la respuesta JSON de las APIs.";
   chatEl.appendChild(p);
}

function removeEmptyHint() {
   chatEl.querySelector(".empty-hint")?.remove();
}

function setFile(file) {
   selectedFile = file;
   if (file) {
      fileChip.hidden = false;
      fileChip.textContent = file.name;
   } else {
      fileChip.hidden = true;
      fileChip.textContent = "";
      fileInput.value = "";
   }
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
   if (!selectedFile && !text) return;

   saveUrls();
   removeEmptyHint();

   const recBase = baseUrl(urlRecognition);
   const careBase = baseUrl(urlCare);

   if (selectedFile) {
      const userLines = [];
      if (text) userLines.push(text);
      userLines.push(`[imagen: ${selectedFile.name}]`);
      appendMessage("user", "Tú", userLines.join("\n"));

      btnSend.disabled = true;
      try {
         const { ok, status, data } = await sendRecognition(
            selectedFile,
            recBase
         );
         const raw = JSON.stringify(data, null, 2);
         appendMessage(
            "assistant",
            ok ? "Reconocimiento (raw JSON)" : `Error HTTP ${status}`,
            raw,
            true,
            !ok
         );
      } catch (e) {
         appendMessage(
            "assistant",
            "Error de red",
            String(e.message || e),
            true,
            true
         );
      } finally {
         btnSend.disabled = false;
         inputEl.value = "";
         setFile(null);
         autoResize();
      }
      return;
   }

   appendMessage("user", "Tú", text);
   inputEl.value = "";
   autoResize();
   btnSend.disabled = true;

   try {
      const { ok, status, data } = await sendPlantCare(text, careBase);
      const raw = JSON.stringify(data, null, 2);
      appendMessage(
         "assistant",
         ok ? "Cuidados / búsqueda (raw JSON)" : `Error HTTP ${status}`,
         raw,
         true,
         !ok
      );
   } catch (e) {
      appendMessage(
         "assistant",
         "Error de red",
         String(e.message || e),
         true,
         true
      );
   } finally {
      btnSend.disabled = false;
   }
}

function autoResize() {
   inputEl.style.height = "auto";
   inputEl.style.height = `${Math.min(inputEl.scrollHeight, 128)}px`;
}

btnSend.addEventListener("click", onSend);
inputEl.addEventListener("keydown", (e) => {
   if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
   }
});
inputEl.addEventListener("input", autoResize);

btnAttach.addEventListener("click", () => fileInput.click());
fileInput.addEventListener("change", () => {
   const f = fileInput.files?.[0];
   setFile(f || null);
});

btnSettings.addEventListener("click", () => {
   const open = settingsPanel.hidden;
   settingsPanel.hidden = !open;
   btnSettings.setAttribute("aria-expanded", String(open));
   if (open) saveUrls();
});

urlRecognition.addEventListener("change", saveUrls);
urlCare.addEventListener("change", saveUrls);

loadUrls();
showEmptyHint();
