import { useState } from "react";

function ChatInput({ onSend, disabled }) {
    const [message, setMessage] = useState("");

    const handleSubmit = () => {
        const trimmedMessage = message.trim();

        if (!trimmedMessage || disabled) {
            return;
        }

        onSend(trimmedMessage);
        setMessage("");
    };

    const handleKeyDown = (event) => {
        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {
            event.preventDefault();
            handleSubmit();
        }
    };

    return (
        <div className="chat-input-container">
            <textarea
                value={message}
                onChange={(event) =>
                    setMessage(event.target.value)
                }
                onKeyDown={handleKeyDown}
                placeholder="Message..."
                disabled={disabled}
                rows={1}
            />

            <button
                onClick={handleSubmit}
                disabled={
                    disabled || !message.trim()
                }
            >
                Send
            </button>
        </div>
    );
}

export default ChatInput;