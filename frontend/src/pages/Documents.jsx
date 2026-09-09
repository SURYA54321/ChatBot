import { useEffect, useState } from "react";
import toast from "react-hot-toast";

import {
    getDocuments,
    uploadDocument,
    deleteDocument,
} from "../api/documentApi";

function Documents() {
    const [documents, setDocuments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [uploading, setUploading] = useState(false);

    const loadDocuments = async () => {
        try {
            setLoading(true);

            const data = await getDocuments();

            setDocuments(data);
        } catch (error) {
            console.error(error);
            toast.error("Failed to load documents");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadDocuments();
    }, []);

    const handleUpload = async (event) => {
        const file = event.target.files?.[0];

        if (!file) {
            return;
        }

        try {
            setUploading(true);

            const document = await uploadDocument(file);

            setDocuments((prev) => [
                document,
                ...prev,
            ]);

            toast.success("Document uploaded");
        } catch (error) {
            console.error(error);

            toast.error(
                error.response?.data?.detail ||
                    "Failed to upload document"
            );
        } finally {
            setUploading(false);

            // Allow selecting the same file again
            event.target.value = "";
        }
    };

    const handleDelete = async (documentId) => {
        const confirmed = window.confirm(
            "Delete this document?"
        );

        if (!confirmed) {
            return;
        }

        try {
            await deleteDocument(documentId);

            setDocuments((prev) =>
                prev.filter(
                    (document) =>
                        document.id !== documentId
                )
            );

            toast.success("Document deleted");
        } catch (error) {
            console.error(error);

            toast.error(
                "Failed to delete document"
            );
        }
    };

    return (
        <main className="documents-page">
            <header className="documents-header">
                <div>
                    <h1>Documents</h1>
                    <p>
                        Upload documents for your
                        chatbot to use as knowledge.
                    </p>
                </div>

                <label className="upload-button">
                    {uploading
                        ? "Uploading..."
                        : "Upload Document"}

                    <input
                        type="file"
                        accept=".pdf,.txt,.docx,.md,.csv"
                        onChange={handleUpload}
                        disabled={uploading}
                        hidden
                    />
                </label>
            </header>

            {loading ? (
                <div className="documents-loading">
                    Loading documents...
                </div>
            ) : documents.length === 0 ? (
                <div className="documents-empty">
                    <h2>No documents yet</h2>
                    <p>
                        Upload a PDF, TXT, DOCX, MD,
                        or CSV file.
                    </p>
                </div>
            ) : (
                <div className="documents-list">
                    {documents.map((document) => (
                        <div
                            className="document-card"
                            key={document.id}
                        >
                            <div>
                                <h3>
                                    {document.name}
                                </h3>

                                <p>
                                    {document.file_type ||
                                        "Unknown type"}
                                </p>

                                <span
                                    className={`document-status ${document.status}`}
                                >
                                    {document.status}
                                </span>
                            </div>

                            <button
                                onClick={() =>
                                    handleDelete(
                                        document.id
                                    )
                                }
                                disabled={
                                    document.status ===
                                    "processing"
                                }
                            >
                                Delete
                            </button>
                        </div>
                    ))}
                </div>
            )}
        </main>
    );
}

export default Documents;