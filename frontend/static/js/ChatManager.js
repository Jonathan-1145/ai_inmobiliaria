export function createChatManager({ sessionId, StatusIndicatorManager }) {
    return {
        async send(message) {
            let timeoutId;
            let retries = 0;
            const maxRetries = 2;

            // Obtener tokens de manera segura
            const { apiToken } = await getTokensFromSecureEndpoint();

            const tryFetch = async () => {
                try {
                    StatusIndicatorManager.show("Preparando respuesta...", "info");

                    timeoutId = setTimeout(() => {
                        StatusIndicatorManager.show("Pensando... esto puede tardar unos segundos", "info");
                    }, 4000);

                    const response = await fetch("/chat", {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            "Authorization": `Bearer ${apiToken}`
                        },
                        body: JSON.stringify({
                            session_id: sessionId,
                            message
                        })
                    });

                    clearTimeout(timeoutId);
                    StatusIndicatorManager.hide();

                    if (!response.ok) throw new Error("Error en el servidor");

                    const data = await response.json();
                    return data.response;

                } catch (err) {
                    clearTimeout(timeoutId);
                    retries += 1;

                    if (!navigator.onLine) {
                        StatusIndicatorManager.show("Sin conexión. Verifica tu red.", "error");
                        return "⚠️ No tienes conexión a internet.";
                    }

                    if (retries <= maxRetries) {
                        StatusIndicatorManager.show("Reintentando conexión...", "warning");
                        return await tryFetch();
                    }

                    console.error("[ChatManager] Error:", err);
                    StatusIndicatorManager.show("Fallo al obtener respuesta", "error");
                    return "⚠️ Ocurrió un error procesando tu mensaje. Intenta de nuevo.";
                }
            };

            return await tryFetch();
        }
    };
}

// Obtener el webToken desde las cabeceras
async function getWebTokenFromHeaders() {
    try {
        const response = await fetch("/get-token");
        if (!response.ok) throw new Error("No se pudo obtener webToken");

        const webToken = response.headers.get("X-Web-Authorization-Token");
        if (!webToken) throw new Error("webToken no encontrado en cabeceras");

        return webToken;
    } catch (error) {
        console.error("Error al obtener webToken:", error);
        throw new Error("Error al obtener webToken");
    }
}

// Obtener los tokens de manera segura
async function getTokensFromSecureEndpoint() {
    const webToken = await getWebTokenFromHeaders();

    const response = await fetch("/token/onlyjs", {
        headers: {
            "Authorization": `Bearer ${webToken}`
        }
    });

    if (!response.ok) throw new Error("Fallo al obtener tokens de /token/onlyjs");

    const { apiToken, webToken: refreshedWebToken } = await response.json();
    if (!apiToken || !refreshedWebToken) throw new Error("Tokens inválidos");

    return { apiToken, webToken: refreshedWebToken };
}
