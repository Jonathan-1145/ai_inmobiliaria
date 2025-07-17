export function createStatusIndicatorManager() {
    const el = document.getElementById("status-indicator");

    return {
        show(message, type = "info") {
            if (!el) return;
            el.textContent = message;
            el.className = `status-indicator ${type}`;
            el.style.display = "block";
        },
        hide() {
            if (el) el.style.display = "none";
        }
    };
}
