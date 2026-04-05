(function () {
   "use strict";

   const STORAGE_KEY = "gaia_username";

   const form = document.getElementById("login-form");
   const input = document.getElementById("username-input");

   if (localStorage.getItem(STORAGE_KEY)) {
      window.location.href = "index.html";
      return;
   }

   form.addEventListener("submit", (e) => {
      e.preventDefault();
      const name = input.value.trim();
      if (name) {
         localStorage.setItem(STORAGE_KEY, name);
         window.location.href = "index.html";
      }
   });
})();
