import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

function MessageBubble({
    message,
    onRetry,
}) {
    const isUser =
        message.role === "user";

    return (
        <div
            className={`message-bubble ${
                isUser
                    ? "user-message"
                    : "assistant-message"
            }`}
        >
            <div className="message-role">
                {isUser
                    ? "You"
                    : "Assistant"}
            </div>

            <div className="message-content">
                {isUser ? (
                    message.content
                ) : (
                    <ReactMarkdown
                        remarkPlugins={[
                            remarkGfm,
                        ]}
                    >
                        {message.content}
                    </ReactMarkdown>
                )}
            </div>

            {message.error && (
                <button
                    className="retry-button"
                    onClick={() =>
                        onRetry(message)
                    }
                >
                    Retry
                </button>
            )}

            {!isUser &&
                message.sources &&
                message.sources.length >
                    0 && (
                    <div className="message-sources">
                        <div className="sources-title">
                            Sources
                        </div>

                        <div className="sources-list">
                            {message.sources.map(
                                (
                                    source,
                                    index
                                ) => (
                                    <div
                                        className="source-item"
                                        key={`${source.document_id}-${source.page}-${index}`}
                                    >
                                        <span className="source-name">
                                            {
                                                source.filename
                                            }
                                        </span>

                                        {source.page && (
                                            <span className="source-page">
                                                Page{" "}
                                                {
                                                    source.page
                                                }
                                            </span>
                                        )}
                                    </div>
                                )
                            )}
                        </div>
                    </div>
                )}
        </div>
    );
}

export default MessageBubble;
