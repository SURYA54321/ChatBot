import api from "./axios";

export const getConversations =
    async () => {
        const response = await api.get(
            "/conversations/"
        );

        return response.data;
    };

export const createConversation =
    async (title = "New Chat") => {
        const response = await api.post(
            "/conversations/",
            {
                title,
            }
        );

        return response.data;
    };

export const getConversationMessages =
    async (conversationId) => {
        const response = await api.get(
            `/conversations/${conversationId}/messages/`
        );

        return response.data;
    };

export const updateConversation =
    async (conversationId, data) => {
        const response = await api.patch(
            `/conversations/${conversationId}/`,
            data
        );

        return response.data;
    };

export const deleteConversation =
    async (conversationId) => {
        await api.delete(
            `/conversations/${conversationId}/`
        );
    };