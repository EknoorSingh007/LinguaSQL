document.addEventListener("DOMContentLoaded", async () => {
  const cards = document.querySelectorAll(".table-card");

  for (const card of cards) {
    const tableName = card.dataset.name;
    try {
      const res = await fetch(`/columns/${tableName}`);
      if (!res.ok) throw new Error();
      const cols = await res.json();
      const colCount = Object.keys(cols).length;
      card.title = `${colCount} column${colCount !== 1 ? 's' : ''}`;
    } catch {
      card.title = `Table: ${tableName}`;
    }
  }
});
