import { createUIManager } from './UIManager.js';
import { createChatManager } from './ChatManager.js';
import { createStatusIndicatorManager } from './StatusIndicatorManager.js';
import { createTypingIndicatorManager } from './TypingIndicatorManager.js';

const maxChars = 1500;
const shouldAutoScroll = { value: true };

export function App() {
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatContainer = document.querySelector(".chat-message-container");
    const chatMessages = document.getElementById("chat-messages");
    const placeholder = document.getElementById("chat-placeholder");
    const charCounter = document.getElementById("char-counter");
    const sendButton = document.getElementById("send-button");

    const UIManager = createUIManager({
        chatMessages,
        chatContainer,
        placeholder,
        userInput,
        charCounter,
        sendButton,
        maxChars,
        shouldAutoScrollRef: shouldAutoScroll
    });

    const sessionId = (() => {
        const key = "homecat_session_id";
        let id = localStorage.getItem(key);
        if (!id) {
            id = crypto.randomUUID();
            localStorage.setItem(key, id);
        }
        return id;
    })();

    const StatusIndicatorManager = createStatusIndicatorManager();
    const ChatManager = createChatManager({ sessionId, StatusIndicatorManager });
    const TypingIndicatorManager = createTypingIndicatorManager();

    const onSubmit = async (e) => {
        e.preventDefault();

        const message = userInput.value.trim();
        if (!message) {
            UIManager.markInputError("No puedes enviar un mensaje vacío.");
            return;
        }
        UIManager.clearInputError();

        UIManager.disableInput(); // Bloquea el input mientras responde

        UIManager.appendMessage(message, "user");
        UIManager.clearInput();
        UIManager.updateCounter();
        TypingIndicatorManager.show();

        try {
            const response = await ChatManager.send(message);
            UIManager.appendMessage(response, "bot");
            setTimeout(() => UIManager.scrollToBottom(), 50);
        } catch (err) {
            console.error("[Chat Error]:", err);
            UIManager.appendMessage("⚠️ Ocurrió un error procesando tu mensaje. Intenta de nuevo.", "bot");
        } finally {
            TypingIndicatorManager.hide();
            UIManager.enableInput(); // Rehabilita input y botón
        }
    };

    function init() {
        UIManager.bindInputEvents();
        UIManager.togglePlaceholder();
        TypingIndicatorManager.hide();

        chatForm.addEventListener("submit", onSubmit);

        userInput.addEventListener("keydown", function (event) {
            if (userInput.disabled) return;

            if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault();
                chatForm.dispatchEvent(new Event("submit", { bubbles: true, cancelable: true }));
            }
        });
    }

    return { init };
}
