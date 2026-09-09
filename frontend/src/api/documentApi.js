import api from "./axios";

export const getDocuments =
    async () => {
        const response = await api.get(
            "/documents/"
        );

        return response.data;
    };

export const uploadDocument =
    async (file) => {
        const formData = new FormData();

        formData.append("file", file);

        const response = await api.post(
            "/documents/",
            formData,
            {
                headers: {
                    "Content-Type":
                        "multipart/form-data",
                },
            }
        );

        return response.data;
    };

export const deleteDocument =
    async (documentId) => {
        await api.delete(
            `/documents/${documentId}/`
        );
    };