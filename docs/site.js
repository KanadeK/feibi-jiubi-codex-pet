const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

function useStillImages() {
  document.querySelectorAll("img[data-still]").forEach((image) => {
    image.src = image.dataset.still;
  });
}

function revealContent() {
  const elements = document.querySelectorAll(".reveal");
  if (reduceMotion.matches || !("IntersectionObserver" in window)) {
    elements.forEach((element) => element.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { rootMargin: "0px 0px -8%", threshold: 0.12 },
  );

  elements.forEach((element) => observer.observe(element));
}

function handleImageErrors() {
  document.querySelectorAll("img").forEach((image) => {
    image.addEventListener("error", () => {
      image.classList.add("asset-error");
      image.alt = "预览加载失败，请在 GitHub 仓库查看原始素材。";
    });
  });
}

if (reduceMotion.matches) useStillImages();
reduceMotion.addEventListener?.("change", (event) => {
  if (event.matches) useStillImages();
});

handleImageErrors();
revealContent();
