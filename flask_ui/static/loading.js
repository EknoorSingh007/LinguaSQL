document.addEventListener("DOMContentLoaded", () => {
  const spinner = document.getElementById("loading-spinner");
  const nlqForm = document.getElementById("nlq-form");
  if (!nlqForm || !spinner) return;

  nlqForm.addEventListener("submit", () => {
    spinner.style.display = "block";
  });
});