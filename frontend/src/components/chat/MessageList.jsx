import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";

function MessageList({ messages, onRetry }) {
    const containerRef = useRef(null);
    const bottomRef = useRef(null);
    const isAtBottomRef = useRef(true);


    const handleScroll = () => {
        const el = containerRef.current;
        if (!el) return;

        const distanceFromBottom =
            el.scrollHeight - el.scrollTop - el.clientHeight;

        isAtBottomRef.current = distanceFromBottom < 80;
    };

    useEffect(() => {
        const el = containerRef.current;
        if (!el || !isAtBottomRef.current) return;
        el.scrollTop = el.scrollHeight;
    }, [messages]);

    return (
        <div
            className="message-list"
            ref={containerRef}
            onScroll={handleScroll}
        >
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