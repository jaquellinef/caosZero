/* CaosZero 2.0 — interações da página */
(function () {
  "use strict";

  const root = document.documentElement;
  const themeButton = document.querySelector(".theme-toggle");
  const navToggle = document.querySelector(".nav-toggle");
  const nav = document.getElementById("menu-principal");
  const topbar = document.querySelector(".topbar");

  /* ---------- Tema ---------- */
  const stored = localStorage.getItem("caoszero-theme");
  if (stored === "light" || stored === "dark") {
    root.dataset.theme = stored;
  }

  if (themeButton) {
    themeButton.addEventListener("click", function () {
      const next = root.dataset.theme === "dark" ? "light" : "dark";
      root.dataset.theme = next;
      localStorage.setItem("caoszero-theme", next);
      themeButton.setAttribute(
        "aria-label",
        next === "dark" ? "Ativar tema claro" : "Ativar tema escuro"
      );
    });
  }

  /* ---------- Menu mobile ---------- */
  function closeMenu() {
    if (!nav || !navToggle) return;
    nav.classList.remove("is-open");
    navToggle.setAttribute("aria-expanded", "false");
    navToggle.setAttribute("aria-label", "Abrir menu");
  }

  if (navToggle && nav) {
    navToggle.addEventListener("click", function () {
      const open = nav.classList.toggle("is-open");
      navToggle.setAttribute("aria-expanded", String(open));
      navToggle.setAttribute("aria-label", open ? "Fechar menu" : "Abrir menu");
    });

    nav.addEventListener("click", function (event) {
      if (event.target.closest("a")) closeMenu();
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") closeMenu();
    });
  }

  /* ---------- Topbar ao rolar ---------- */
  function onScroll() {
    if (!topbar) return;
    topbar.classList.toggle("is-scrolled", window.scrollY > 8);
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  /* ---------- Copiar comandos ---------- */
  function textOf(targetId) {
    const target = document.getElementById(targetId);
    return target ? target.innerText.trim() : "";
  }

  async function copyText(text, button) {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
      } else {
        const area = document.createElement("textarea");
        area.value = text;
        area.setAttribute("readonly", "");
        area.style.position = "fixed";
        area.style.opacity = "0";
        document.body.appendChild(area);
        area.select();
        document.execCommand("copy");
        document.body.removeChild(area);
      }

      const original = button.textContent;
      button.textContent = "copiado!";
      button.classList.add("is-copied");
      window.setTimeout(function () {
        button.textContent = original;
        button.classList.remove("is-copied");
      }, 1600);
    } catch (error) {
      button.textContent = "falhou";
      window.setTimeout(function () {
        button.textContent = "copiar";
      }, 1600);
    }
  }

  document.querySelectorAll("[data-copy-target]").forEach(function (button) {
    button.addEventListener("click", function () {
      const targetId = button.getAttribute("data-copy-target");
      copyText(textOf(targetId), button);
    });
  });

  /* ---------- Reveal on scroll ---------- */
  const revealItems = document.querySelectorAll(".reveal");

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-visible");
            observer.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12, rootMargin: "0px 0px -40px 0px" }
    );

    revealItems.forEach(function (item) {
      observer.observe(item);
    });
  } else {
    revealItems.forEach(function (item) {
      item.classList.add("is-visible");
    });
  }

  /* ---------- Navegação ativa ---------- */
  const sections = Array.from(document.querySelectorAll("main section[id]"));
  const navLinks = Array.from(document.querySelectorAll('.nav a[href^="#"]'));

  if ("IntersectionObserver" in window && sections.length && navLinks.length) {
    const active = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          const id = entry.target.getAttribute("id");
          navLinks.forEach(function (link) {
            link.classList.toggle("is-active", link.getAttribute("href") === "#" + id);
          });
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );

    sections.forEach(function (section) {
      active.observe(section);
    });
  }

  /* ---------- Ano do rodapé ---------- */
  const year = document.getElementById("ano");
  if (year) year.textContent = String(new Date().getFullYear());
})();
