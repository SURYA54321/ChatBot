import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";

function MessageList({
    messages,
    onRetry,
}) {
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({
            behavior: "smooth",
        });
    }, [messages]);

    return (
        <div className="message-list">
            {messages.map((message) => (
                <MessageBubble
                    key={message.id}
                    message={message}
                    onRetry={onRetry}
                />
            ))}

            <div ref={bottomRef} />
        </div>
    );
}

export default MessageList;
