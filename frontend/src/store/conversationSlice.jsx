import { createSlice } from "@reduxjs/toolkit";

const initialState = {
    conversations: [],
    selectedConversationId: null,
};

const conversationSlice = createSlice({
    name: "conversations",
    initialState,

    reducers: {
        setConversations: (state, action) => {
            state.conversations = action.payload;
        },

        addConversation: (state, action) => {
            state.conversations.unshift(
                action.payload
            );
        },

        removeConversation: (state, action) => {
            state.conversations =
                state.conversations.filter(
                    (conversation) =>
                        conversation.id !==
                        action.payload
                );

            if (
                state.selectedConversationId ===
                action.payload
            ) {
                state.selectedConversationId = null;
            }
        },

        updateConversation: (state, action) => {
            const index =
                state.conversations.findIndex(
                    (conversation) =>
                        conversation.id ===
                        action.payload.id
                );

            if (index !== -1) {
                state.conversations[index] = {
                    ...state.conversations[index],
                    ...action.payload,
                };
            }
        },

        setSelectedConversation: (
            state,
            action
        ) => {
            state.selectedConversationId =
                action.payload;
        },

        clearConversations: (state) => {
            state.conversations = [];
            state.selectedConversationId = null;
        },
    },
});

export const {
    setConversations,
    addConversation,
    removeConversation,
    updateConversation,
    setSelectedConversation,
    clearConversations,
} = conversationSlice.actions;

export default conversationSlice.reducer;