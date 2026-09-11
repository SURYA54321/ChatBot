import { useEffect, useRef, useState } from "react";
import toast from "react-hot-toast";

import {
    getDocuments,
    uploadDocument,
    deleteDocument,
} from "../../api/documentApi";

function ChatInput({ onSend, disabled, conversationId }) {
    const [message, setMessage] = useState("");
    const [documents, setDocuments] = useState([]);
    const [uploading, setUploading] = useState(false);

    const fileInputRef = useRef(null);

    // >>> NEW: load this chat's documents whenever the selected
    // conversation changes, so switching chats shows the right
    // attachments (not a stale list from the previous chat).
    useEffect(() => {
        if (!conversationId) {
            setDocuments([]);
            return;
        }

        const loadDocuments = async () => {
            try {
                const data = await getDocuments(conversationId);
                setDocuments(data);
            } catch (error) {
                console.error(error);
                toast.error("Failed to load documents");
            }
        };

        loadDocuments();
    }, [conversationId]);

    const handleAttachClick = () => {
        fileInputRef.current?.click();
    };

    const handleFileChange = async (event) => {
        const file = event.target.files?.[0];

        if (!file) {
            return;
        }

        try {
            setUploading(true);

            const document = await uploadDocument(
                file,
                conversationId
            );

            setDocuments((prev) => [document, ...prev]);

            if (document.status === "failed") {
                toast.error(
                    `Failed to process "${document.name}"`
                );
            } else {
                toast.success(
                    `"${document.name}" added to this chat`
                );
            }
        } catch (error) {
            console.error(error);

            // >>> The backend still returns the (failed) document
            // record even on a 500, so we can show it as a failed
            // chip instead of just silently losing it.
            const failedDocument =
                error.response?.data?.document;

            if (failedDocument) {
                setDocuments((prev) => [
                    failedDocument,
                    ...prev,
                ]);
            }

            toast.error(
                error.response?.data?.detail ||
                    "Failed to upload document"
            );
        } finally {
            setUploading(false);
            event.target.value = "";
        }
    };

    const handleDeleteDocument = async (documentId) => {
        try {
            await deleteDocument(documentId);

            setDocuments((prev) =>
                prev.filter(
                    (document) => document.id !== documentId
                )
            );
        } catch (error) {
            console.error(error);
            toast.error("Failed to delete document");
        }
    };

    const handleSubmit = () => {
        const trimmedMessage = message.trim();

        if (!trimmedMessage || disabled) {
            return;
        }

        onSend(trimmedMessage);
        setMessage("");
    };

    const handleKeyDown = (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            handleSubmit();
        }
    };

    return (
        <div className="chat-input-wrapper">
            {documents.length > 0 && (
                <div className="chat-attachments">
                    {documents.map((document) => (
                        <div
                            className={`attachment-chip attachment-${document.status}`}
                            key={document.id}
                        >
                            <span className="attachment-name">
                                {document.name}
                            </span>

                            <span className="attachment-status">
                                {document.status}
                            </span>

                            <button
                                type="button"
                                className="attachment-remove"
                                onClick={() =>
                                    handleDeleteDocument(
                                        document.id
                                    )
                                }
                            >
                                ×
                            </button>
                        </div>
                    ))}
                </div>
            )}

            <div className="chat-input-container">
                <button
                    type="button"
                    className="attach-button"
                    onClick={handleAttachClick}
                    disabled={uploading}
                    title="Attach a document to this chat"
                >
                    {uploading ? "…" : "+"}
                </button>

                <input
                    type="file"
                    ref={fileInputRef}
                    accept=".pdf,.txt,.docx,.md,.csv"
                    onChange={handleFileChange}
                    disabled={uploading}
                    hidden
                />

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
                    disabled={disabled || !message.trim()}
                >
                    Send
                </button>
            </div>
        </div>
    );
}

export default ChatInput;