import { getHoraActual } from './utils.js';

export function createUIManager({
    chatMessages,
    chatContainer,
    placeholder,
    userInput,
    charCounter,
    sendButton,
    maxChars
}) {

    const disableInput = () => {
        userInput.disabled = true;
        sendButton.disabled = true;
    };

    const enableInput = () => {
        userInput.disabled = false;
        updateCounter();
    };

    const markInputError = (msg) => {
        userInput.classList.add("input-error");

        let errorEl = document.getElementById("input-error-msg");
        if (!errorEl) {
            errorEl = document.createElement("div");
            errorEl.id = "input-error-msg";
            errorEl.className = "input-error-message";
            userInput.parentNode.appendChild(errorEl);
        }
        errorEl.textContent = msg;
        errorEl.style.display = "block";
    };

    const clearInputError = () => {
        userInput.classList.remove("input-error");

        const errorEl = document.getElementById("input-error-msg");
        if (errorEl) {
            errorEl.style.display = "none";
        }
    };

    const updateCounter = () => {
        const trimmed = userInput.value.slice(0, maxChars);
        if (userInput.value.length > maxChars) {
            userInput.value = trimmed;
        }

        const currentLength = userInput.value.length;
        charCounter.textContent = `${currentLength} / ${maxChars}`;
        sendButton.disabled = currentLength === 0;

        charCounter.classList.remove("safe", "warning", "danger", "full");

        if (currentLength >= maxChars) {
            charCounter.classList.add("full");
        } else if (currentLength >= maxChars * 0.9) {
            charCounter.classList.add("danger");
        } else if (currentLength >= maxChars * 0.6) {
            charCounter.classList.add("warning");
        } else {
            charCounter.classList.add("safe");
        }

        if (currentLength === 0 || currentLength > maxChars) {
            //markInputError("El mensaje está vacío o excede el límite.");
        } else {
            clearInputError();
        }
    };

    const initAutoScroll = () => {
        const scrollParent = document.getElementById("chat-messages");
        const chatContainer = document.querySelector(".chat-message-container");
        if (!scrollParent || !chatContainer) return;

        const observer = new MutationObserver(() => {
            // Espera a que se rendericen imágenes o contenido pesado
            setTimeout(() => {
                scrollParent.scrollTop = scrollParent.scrollHeight;
            }, 100);
        });

        observer.observe(chatContainer, {
            childList: true,
            subtree: true
        });

        // Captura cuando se cargan imágenes (incluyendo las lazy)
        document.addEventListener("load", function (e) {
            if (e.target.tagName === "IMG") {
                scrollParent.scrollTop = scrollParent.scrollHeight;
            }
        }, true);
    };

    const scrollToBottom = () => {
        const scrollParent = document.getElementById("chat-messages");
        if (scrollParent) {
            scrollParent.scrollTop = scrollParent.scrollHeight;
        }
    };

    initAutoScroll();

    const appendMessage = (text, type = "user") => {
        const wrapper = document.createElement("div");
        wrapper.classList.add("message", `${type}-message`);

        const bubble = document.createElement("div");
        bubble.classList.add("message-content");

        if (text.startsWith("⚠️")) {
            bubble.classList.add("error-message");
        }

        const formatted = text
            .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
            .replace(/\n/g, "<br>");

        bubble.innerHTML = `<div class="bubble-text">${formatted}</div>`;
        wrapper.appendChild(bubble);

        // Hora bajo el mensaje, siempre alineada según tipo
        const timestamp = document.createElement("div");
        timestamp.classList.add("timestamp", "no-copy");
        timestamp.textContent = getHoraActual().replace(/[\[\]]/g, "").replace(/^0/, '');
        wrapper.appendChild(timestamp);

        chatContainer.appendChild(wrapper);
        scrollToBottom();
        togglePlaceholder();
    };

    const togglePlaceholder = () => {
        if (!placeholder) return;
        const hasMessages = chatContainer.children.length > 0;
        placeholder.style.display = hasMessages ? "none" : "flex";
    };

    const clearInput = () => {
        userInput.value = "";
        userInput.focus();
        updateCounter();
    };

    const bindInputEvents = () => {
        userInput.addEventListener("input", updateCounter);
        userInput.addEventListener("paste", () => setTimeout(updateCounter, 0));
        updateCounter();
    };

    return {
        appendMessage,
        togglePlaceholder,
        scrollToBottom,
        clearInput,
        bindInputEvents,
        updateCounter,
        markInputError,
        clearInputError,
        disableInput,
        enableInput
    };

}