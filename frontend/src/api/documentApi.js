import api from "./axios";

export const getDocuments = async (conversationId) => {
    const response = await api.get("/documents/", {
        params: {
            conversation_id: conversationId,
        },
    });

    return response.data;
};

export const uploadDocument = async (file, conversationId) => {
    const formData = new FormData();

    formData.append("file", file);
    formData.append("conversation", conversationId);

    const response = await api.post(
        "/documents/",
        formData,
        {
            headers: {
                "Content-Type": "multipart/form-data",
            },
        }
    );

    return response.data;
};

export const deleteDocument = async (documentId) => {
    await api.delete(`/documents/${documentId}/`);
};