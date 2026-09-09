import Sidebar from "../components/chat/Sidebar";
import ChatWindow from "../components/chat/ChatWindow";

function Chat() {
    return (
        <div className="chat-layout">
            <Sidebar />
            <ChatWindow />
        </div>
    );
}

export default Chat;