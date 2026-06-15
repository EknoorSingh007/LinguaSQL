document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.getElementById("table-search");
  const cards = document.querySelectorAll(".table-card");

  if (!searchInput) return;

  searchInput.addEventListener("input", () => {
    const q = searchInput.value.trim().toLowerCase();
    cards.forEach(card => {
      const name = card.dataset.name;  // using dataset API
      card.style.display = name.includes(q) ? "" : "none";
    });
  });
})