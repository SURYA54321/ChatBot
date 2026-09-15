// Claude

import { useEffect, useState } from "react";
import { useSelector } from "react-redux";
import toast from "react-hot-toast";

import {
  getConversationMessages,
  updateConversation,
} from "../../api/conversationApi";

import { streamMessage } from "../../api/chatApi";

import MessageList from "./MessageList";
import ChatInput from "./ChatInput";

function ChatWindow() {
  const conversationId = useSelector(
    (state) => state.conversations.selectedConversationId,
  );

  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!conversationId) {
      setMessages([]);
      return;
    }

    const loadMessages = async () => {
      try {
        setLoading(true);

        const data = await getConversationMessages(conversationId);

        setMessages(data);
      } catch (error) {
        console.error(error);
        toast.error("Failed to load messages");
      } finally {
        setLoading(false);
      }
    };

    loadMessages();
  }, [conversationId]);

  const handleSend = async (message, isRetry = false) => {
    if (!conversationId || !message.trim() || loading) {
      return;
    }

    let assistantMessageId;

    if (!isRetry) {
      const userMessage = {
        id: `temp-${Date.now()}`,
        role: "user",
        content: message,
      };

      setMessages((prev) => [...prev, userMessage]);

      assistantMessageId = `assistant-${Date.now()}`;

      const assistantMessage = {
        id: assistantMessageId,
        role: "assistant",
        content: "",
        streaming: true,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } else {
      assistantMessageId = `assistant-${Date.now()}`;

      const assistantMessage = {
        id: assistantMessageId,
        role: "assistant",
        content: "",
        streaming: true,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    }

    try {
      setLoading(true);

      await streamMessage(
        conversationId,
        message,

        (token) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? { ...msg, content: msg.content + token }
                : msg,
            ),
          );
        },

        async (data) => {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === assistantMessageId
                ? {
                    ...msg,
                    streaming: false,
                    ...(data.sources ? { sources: data.sources } : {}),
                  }
                : msg,
            ),
          );

          if (!isRetry && messages.length === 0) {
            try {
              const title = message.trim().slice(0, 40);

              await updateConversation(conversationId, {
                title,
              });
            } catch (error) {
              console.error("Failed to update conversation title:", error);
            }
          }
        },
      );
    } catch (error) {
      console.error("Chat error:", error);

      setMessages((currentMessages) =>
        currentMessages.map((msg) =>
          msg.id === assistantMessageId
            ? {
                ...msg,
                content: "Something went wrong. Please try again.",
                error: true,
                streaming: false,
              }
            : msg,
        ),
      );

      toast.error(error.message || "Failed to send message");
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = async (failedMessage) => {
    const failedIndex = messages.findIndex(
      (message) => message.id === failedMessage.id,
    );

    if (failedIndex === -1) {
      return;
    }

    const userMessage = messages[failedIndex - 1];

    if (!userMessage || userMessage.role !== "user") {
      return;
    }

    setMessages((currentMessages) =>
      currentMessages.map((message) =>
        message.id === failedMessage.id
          ? { ...message, content: "", error: false, streaming: false }
          : message,
      ),
    );

    await handleSend(userMessage.content, true);
  };

  return (
    <main className="chat-window">
      <header className="chat-header">
        <h2>{conversationId ? "Chat" : "New Chat"}</h2>
      </header>

      {!conversationId ? (
        <div className="empty-chat">
          <h2>Start a conversation</h2>
          <p>Ask questions about your documents.</p>
        </div>
      ) : (
        <>
          <MessageList messages={messages} onRetry={handleRetry} />

          <ChatInput
            onSend={handleSend}
            disabled={loading}
            conversationId={conversationId}
          />
        </>
      )}
    </main>
  );
}

export default ChatWindow;

// import { useEffect, useState } from "react";
// import { useSelector } from "react-redux";
// import toast from "react-hot-toast";

// import {
//     getConversationMessages,
//     updateConversation,
// } from "../../api/conversationApi";

// import { streamMessage } from "../../api/chatApi";

// import MessageList from "./MessageList";
// import ChatInput from "./ChatInput";

// function ChatWindow() {
//     const conversationId = useSelector(
//         (state) => state.conversations.selectedConversationId
//     );

//     const [messages, setMessages] = useState([]);
//     const [loading, setLoading] = useState(false);

//     useEffect(() => {
//         if (!conversationId) {
//             setMessages([]);
//             return;
//         }

//         const loadMessages = async () => {
//             try {
//                 setLoading(true);

//                 const data = await getConversationMessages(
//                     conversationId
//                 );

//                 setMessages(data);
//             } catch (error) {
//                 console.error(error);
//                 toast.error("Failed to load messages");
//             } finally {
//                 setLoading(false);
//             }
//         };

//         loadMessages();
//     }, [conversationId]);

//     const handleSend = async (message, isRetry = false) => {
//         if (!conversationId || !message.trim() || loading) {
//             return;
//         }

//         let assistantMessageId;

//         if (!isRetry) {
//             const userMessage = {
//                 id: `temp-${Date.now()}`,
//                 role: "user",
//                 content: message,
//             };

//             setMessages((prev) => [...prev, userMessage]);

//             assistantMessageId = `assistant-${Date.now()}`;

//             const assistantMessage = {
//                 id: assistantMessageId,
//                 role: "assistant",
//                 content: "",
//             };

//             setMessages((prev) => [...prev, assistantMessage]);
//         } else {
//             assistantMessageId = `assistant-${Date.now()}`;

//             const assistantMessage = {
//                 id: assistantMessageId,
//                 role: "assistant",
//                 content: "",
//             };

//             setMessages((prev) => [...prev, assistantMessage]);
//         }

//         try {
//             setLoading(true);

//             await streamMessage(
//                 conversationId,
//                 message,

//                 (token) => {
//                     setMessages((prev) =>
//                         prev.map((msg) =>
//                             msg.id === assistantMessageId
//                                 ? { ...msg, content: msg.content + token }
//                                 : msg
//                         )
//                     );
//                 },

//                 async (data) => {
//                     if (data.sources) {
//                         setMessages((prev) =>
//                             prev.map((msg) =>
//                                 msg.id === assistantMessageId
//                                     ? { ...msg, sources: data.sources }
//                                     : msg
//                             )
//                         );
//                     }

//                     if (!isRetry && messages.length === 0) {
//                         try {
//                             const title = message.trim().slice(0, 40);

//                             await updateConversation(conversationId, {
//                                 title,
//                             });
//                         } catch (error) {
//                             console.error(
//                                 "Failed to update conversation title:",
//                                 error
//                             );
//                         }
//                     }
//                 }
//             );
//         } catch (error) {
//             console.error("Chat error:", error);

//             setMessages((currentMessages) =>
//                 currentMessages.map((msg) =>
//                     msg.id === assistantMessageId
//                         ? {
//                               ...msg,
//                               content:
//                                   "Something went wrong. Please try again.",
//                               error: true,
//                           }
//                         : msg
//                 )
//             );

//             toast.error(error.message || "Failed to send message");
//         } finally {
//             setLoading(false);
//         }
//     };

//     const handleRetry = async (failedMessage) => {
//         const failedIndex = messages.findIndex(
//             (message) => message.id === failedMessage.id
//         );

//         if (failedIndex === -1) {
//             return;
//         }

//         const userMessage = messages[failedIndex - 1];

//         if (!userMessage || userMessage.role !== "user") {
//             return;
//         }

//         setMessages((currentMessages) =>
//             currentMessages.map((message) =>
//                 message.id === failedMessage.id
//                     ? { ...message, content: "", error: false }
//                     : message
//             )
//         );

//         await handleSend(userMessage.content, true);
//     };

//     return (
//         <main className="chat-window">
//             <header className="chat-header">
//                 <h2>{conversationId ? "Chat" : "New Chat"}</h2>
//             </header>

//             {!conversationId ? (
//                 <div className="empty-chat">
//                     <h2>Start a conversation</h2>
//                     <p>Ask questions about your documents.</p>
//                 </div>
//             ) : (
//                 <>
//                     <MessageList
//                         messages={messages}
//                         onRetry={handleRetry}
//                     />

//                     {loading && (
//                         <div className="typing-indicator">
//                             <span></span>
//                             <span></span>
//                             <span></span>
//                         </div>
//                     )}

//                     <ChatInput
//                         onSend={handleSend}
//                         disabled={loading}
//                         conversationId={conversationId}
//                     />
//                 </>
//             )}
//         </main>
//     );
// }

// export default ChatWindow;
