import api from "./axios";

export const sendMessage = async (
    conversationId,
    message
) => {
    const response = await api.post("/chat/", {
        conversation_id: conversationId,
        message,
    });

    return response.data;
};

const refreshAccessToken = async () => {
    const refreshToken =
        localStorage.getItem("refresh_token");

    if (!refreshToken) {
        throw new Error("Session expired");
    }

    const response = await fetch(
        `${
            import.meta.env.VITE_BACKEND_URL ||
            "http://127.0.0.1:8000/api"
        }/auth/token/refresh/`,
        {
            method: "POST",
            headers: {
                "Content-Type":
                    "application/json",
            },
            body: JSON.stringify({
                refresh: refreshToken,
            }),
        }
    );

    if (!response.ok) {
        throw new Error("Session expired");
    }

    const data =
        await response.json();

    localStorage.setItem(
        "access_token",
        data.access
    );

    return data.access;
};

export const streamMessage = async (
    conversationId,
    message,
    onToken,
    onDone
) => {
    let accessToken =
        localStorage.getItem("access_token");

    let response = await fetch(
        `${
            import.meta.env.VITE_BACKEND_URL ||
            "http://127.0.0.1:8000/api"
        }/chat/stream/`,
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json",
                Authorization: `Bearer ${accessToken}`,
            },

            body: JSON.stringify({
                conversation_id:
                    conversationId,
                message,
            }),
        }
    );

    // Access token expired
    if (response.status === 401) {
        const newAccessToken =
            await refreshAccessToken();

        accessToken = newAccessToken;

        response = await fetch(
            `${
                import.meta.env
                    .VITE_BACKEND_URL ||
                "http://127.0.0.1:8000/api"
            }/chat/stream/`,
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json",
                    Authorization: `Bearer ${newAccessToken}`,
                },

                body: JSON.stringify({
                    conversation_id:
                        conversationId,
                    message,
                }),
            }
        );
    }

    if (!response.ok) {
        let errorMessage =
            "Failed to send message";

        try {
            const data =
                await response.json();

            errorMessage =
                data.detail ||
                data.message ||
                errorMessage;
        } catch {
            // Ignore invalid JSON
        }

        if (response.status === 401) {
            localStorage.removeItem(
                "access_token"
            );

            localStorage.removeItem(
                "refresh_token"
            );

            window.location.href =
                "/login";

            return;
        }

        throw new Error(errorMessage);
    }

    if (!response.body) {
        throw new Error(
            "Streaming is not supported by this browser."
        );
    }

    const reader =
        response.body.getReader();

    const decoder =
        new TextDecoder();

    let buffer = "";

    while (true) {
        const { value, done } =
            await reader.read();

        if (done) {
            break;
        }

        buffer += decoder.decode(value, {
            stream: true,
        });

        const events =
            buffer.split("\n\n");

        buffer =
            events.pop() || "";

        for (const event of events) {
            if (!event.startsWith("data: ")) {
                continue;
            }

            const jsonString =
                event.slice(6);

            const data =
                JSON.parse(jsonString);

            if (data.type === "token") {
                onToken(data.content);
            }

            if (data.type === "done") {
                onDone?.(data);
            }

            if (data.type === "error") {
                throw new Error(
                    data.content ||
                        "Something went wrong."
                );
            }
        }
    }
};