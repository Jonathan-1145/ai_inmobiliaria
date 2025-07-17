export function createTypingIndicatorManager() {
    const el = document.getElementById("typing-indicator");

    return {
        show() {
            if (el) el.style.display = "flex";
        },
        hide() {
            if (el) el.style.display = "none";
        }
    };
}