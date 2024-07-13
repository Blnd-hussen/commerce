document.addEventListener("DOMContentLoaded", () => {
  const navMenuEl = document.getElementById("nav-menu");

  if (window.innerWidth >= 1000) {
    navMenuEl.classList.remove("hidden");
  }

  window.addEventListener("resize", () => {
    console.log(window.innerWidth);
    if (window.innerWidth >= 1000) {
      navMenuEl.classList.remove("hidden");
    } else {
      navMenuEl.classList.add("hidden");
    }
  });

  document.getElementById("nav-menu-btn").addEventListener("click", () => {
    if (navMenuEl.classList.contains("hidden")) {
      navMenuEl.classList.remove("hidden");
      navMenuEl.classList.add("fade-in");
    } else {
      navMenuEl.classList.remove("fade-in");
      navMenuEl.classList.add("fade-out");
      navMenuEl.addEventListener(
        "animationend",
        function () {
          navMenuEl.classList.add("hidden");
          navMenuEl.classList.remove("fade-out");
        },
        { once: true }
      );
    }
  });
});
