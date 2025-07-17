import { App } from "./App.js";
import { setupLightbox } from "./LightboxManager.js";

// Inicializa todo cuando el DOM esté listo
document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;

    // Verifica si está en la página principal de HomeCat
    if (!body.classList.contains("inicio-homecat-ai")) return;

    // Menú hamburguesa y overlay
    const toggleBtn = document.getElementById("menu-toggle");
    const sidebar = document.querySelector(".sidebar");
    const overlay = document.getElementById("sidebar-overlay");

    if (toggleBtn && sidebar && overlay) {
        function toggleSidebar() {
            sidebar.classList.toggle("visible");
            overlay.classList.toggle("active");
        }

        toggleBtn.addEventListener("click", toggleSidebar);
        overlay.addEventListener("click", toggleSidebar);
    }

    // Scroll para teclado móvil
    const adjustForKeyboard = () => {
        const input = document.getElementById("user-input");
        if (!input) return;

        input.addEventListener("focus", () => {
            if (window.visualViewport) {
                const chatWrapper = document.querySelector(".chat-wrapper");
                const adjust = () => {
                    chatWrapper.style.height = `${window.visualViewport.height}px`;
                };
                adjust();
                window.visualViewport.addEventListener("resize", adjust);
            }
        });

        input.addEventListener("blur", () => {
            const chatWrapper = document.querySelector(".chat-wrapper");
            chatWrapper.style.height = "";
            if (window.visualViewport) {
                window.visualViewport.removeEventListener("resize", adjustForKeyboard);
            }
        });
    };

    // Ejecuta inicializaciones
    const app = App();
    app.init();
    setupLightbox();
    adjustForKeyboard();

    // Ping al backend cada 5 minutos para evitar suspensión en Railway
    setInterval(() => {
        fetch("/health")
            .then((res) => {
                if (!res.ok) console.warn("[PING] Falló el ping al backend");
                else console.log("[PING] Contenedor activo");
            })
            .catch((err) => console.error("[PING] Error:", err));
    }, 5 * 60 * 1000);
});