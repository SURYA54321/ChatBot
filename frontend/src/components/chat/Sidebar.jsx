import { useEffect, useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import {
    getConversations,
    createConversation,
    updateConversation,
    deleteConversation,
} from "../../api/conversationApi";

import {
    setConversations,
    addConversation,
    removeConversation,
    updateConversation as updateConversationState,
    setSelectedConversation,
    clearConversations,
} from "../../store/conversationSlice";

import { logout } from "../../store/authSlice";

function Sidebar() {
    const dispatch = useDispatch();
    const navigate = useNavigate();

    const { conversations, selectedConversationId } = useSelector(
        (state) => state.conversations
    );

    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const loadConversations = async () => {
            try {
                setLoading(true);

                const data = await getConversations();

                dispatch(setConversations(data));
            } catch (error) {
                console.error(error);
                toast.error("Failed to load conversations");
            } finally {
                setLoading(false);
            }
        };

        loadConversations();
    }, [dispatch]);

    const handleNewChat = async () => {
        try {
            const conversation = await createConversation("New Chat");

            dispatch(addConversation(conversation));
            dispatch(setSelectedConversation(conversation.id));
        } catch (error) {
            console.error(error);
            toast.error("Failed to create conversation");
        }
    };

    const handleSelectConversation = (conversationId) => {
        dispatch(setSelectedConversation(conversationId));
    };

    const handleRename = async (conversation) => {
        const title = window.prompt(
            "Enter new title",
            conversation.title
        );

        if (!title?.trim()) {
            return;
        }

        try {
            const updated = await updateConversation(conversation.id, {
                title: title.trim(),
            });

            dispatch(updateConversationState(updated));
        } catch (error) {
            console.error(error);
            toast.error("Failed to rename conversation");
        }
    };

    const handleDelete = async (conversationId) => {
        const confirmed = window.confirm("Delete this conversation?");

        if (!confirmed) {
            return;
        }

        try {
            await deleteConversation(conversationId);

            dispatch(removeConversation(conversationId));
        } catch (error) {
            console.error(error);
            toast.error("Failed to delete conversation");
        }
    };

    const handleLogout = () => {
        dispatch(logout());
        dispatch(clearConversations());

        navigate("/login");
    };

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <h2>RAG Chatbot</h2>
            </div>

            <button className="new-chat-button" onClick={handleNewChat}>
                + New Chat
            </button>

            <div className="conversation-list">
                {loading && (
                    <p className="sidebar-message">Loading chats...</p>
                )}

                {!loading && conversations.length === 0 && (
                    <p className="sidebar-message">
                        No conversations yet.
                    </p>
                )}

                {conversations.map((conversation) => (
                    <div
                        key={conversation.id}
                        className={`conversation-item ${
                            selectedConversationId === conversation.id
                                ? "active"
                                : ""
                        }`}
                        onClick={() =>
                            handleSelectConversation(conversation.id)
                        }
                    >
                        <span>{conversation.title}</span>

                        <div className="conversation-actions">
                            <button
                                onClick={(event) => {
                                    event.stopPropagation();
                                    handleRename(conversation);
                                }}
                            >
                                Rename
                            </button>

                            <button
                                onClick={(event) => {
                                    event.stopPropagation();
                                    handleDelete(conversation.id);
                                }}
                            >
                                Delete
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            <div className="sidebar-footer">
                <button onClick={handleLogout} className="logout-button">
                    Logout
                </button>
            </div>
        </aside>
    );
}

export default Sidebar;