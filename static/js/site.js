document.addEventListener("DOMContentLoaded", () => {
  const yearNode = document.getElementById("currentYear");
  if (yearNode) {
    yearNode.textContent = new Date().getFullYear();
  }

  document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", () => {
      const button = form.querySelector("button[type='submit']");
      if (button && !button.dataset.noDisable) {
        button.disabled = true;
        setTimeout(() => {
          button.disabled = false;
        }, 2500);
      }
    });
  });
});
