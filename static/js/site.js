document.addEventListener("DOMContentLoaded", () => {
  const yearNode = document.getElementById("currentYear");
  if (yearNode) {
    yearNode.textContent = new Date().getFullYear();
  }

  const mobileDrawer = document.getElementById("mobileNavDrawer");
  if (mobileDrawer && window.bootstrap && window.bootstrap.Offcanvas) {
    const offcanvas = window.bootstrap.Offcanvas.getOrCreateInstance(mobileDrawer);
    mobileDrawer.querySelectorAll("a[href]").forEach((link) => {
      link.addEventListener("click", () => {
        offcanvas.hide();
      });
    });
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
