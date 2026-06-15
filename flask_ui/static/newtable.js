const BACKEND = "http://localhost:8000";

document.addEventListener("DOMContentLoaded", () => {
  const btn = document.getElementById("new-table-btn");
  if (!btn) return;

  btn.addEventListener("click", async () => {
    const name = prompt("Enter a name for the new table:");
    if (!name || !name.trim()) return;

    const promptText = `CREATE TABLE ${name.trim()} (id INTEGER PRIMARY KEY);`;

    try {
      const resp = await fetch(`${BACKEND}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: promptText }),
      });
      const data = await resp.json();

      if (resp.ok && data.status === "success") {
        alert(`Table "${name}" created successfully!`);
        window.location.reload();
      } else {
        alert(`Failed to create table:\n${data.detail || JSON.stringify(data)}`);
      }
    } catch (err) {
      alert("Error creating table: " + err);
    }
  });
});