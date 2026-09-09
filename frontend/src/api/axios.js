import axios from "axios";

const api = axios.create({
    baseURL:
        import.meta.env.VITE_BACKEND_URL ||
        "http://127.0.0.1:8000/api",

    headers: {
        "Content-Type": "application/json",
    },
});

let isRefreshing = false;
let refreshSubscribers = [];

const subscribeTokenRefresh = (callback) => {
    refreshSubscribers.push(callback);
};

const onTokenRefreshed = (token) => {
    refreshSubscribers.forEach((callback) =>
        callback(token)
    );

    refreshSubscribers = [];
};

const refreshAccessToken = async () => {
    const refreshToken =
        localStorage.getItem("refresh_token");

    if (!refreshToken) {
        throw new Error("No refresh token");
    }

    const response = await axios.post(
        `${
            import.meta.env.VITE_BACKEND_URL ||
            "http://127.0.0.1:8000/api"
        }/auth/token/refresh/`,
        {
            refresh: refreshToken,
        }
    );

    const newAccessToken =
        response.data.access;

    localStorage.setItem(
        "access_token",
        newAccessToken
    );

    return newAccessToken;
};

// Attach access token
api.interceptors.request.use(
    (config) => {
        const accessToken =
            localStorage.getItem("access_token");

        if (accessToken) {
            config.headers.Authorization =
                `Bearer ${accessToken}`;
        }

        return config;
    },
    (error) => Promise.reject(error)
);

// Handle expired access tokens
api.interceptors.response.use(
    (response) => response,

    async (error) => {
        const originalRequest =
            error.config;

        if (
            error.response?.status !== 401 ||
            originalRequest?._retry
        ) {
            return Promise.reject(error);
        }

        // Don't try to refresh the refresh endpoint
        if (
            originalRequest.url?.includes(
                "/auth/token/refresh/"
            )
        ) {
            localStorage.removeItem(
                "access_token"
            );

            localStorage.removeItem(
                "refresh_token"
            );

            window.location.href = "/login";

            return Promise.reject(error);
        }

        originalRequest._retry = true;

        // Another request is already refreshing
        if (isRefreshing) {
            return new Promise(
                (resolve, reject) => {
                    subscribeTokenRefresh(
                        (token) => {
                            originalRequest.headers.Authorization =
                                `Bearer ${token}`;

                            resolve(
                                api(
                                    originalRequest
                                )
                            );
                        }
                    );
                }
            );
        }

        isRefreshing = true;

        try {
            const newAccessToken =
                await refreshAccessToken();

            isRefreshing = false;

            onTokenRefreshed(
                newAccessToken
            );

            originalRequest.headers.Authorization =
                `Bearer ${newAccessToken}`;

            return api(originalRequest);
        } catch (refreshError) {
            isRefreshing = false;
            refreshSubscribers = [];

            localStorage.removeItem(
                "access_token"
            );

            localStorage.removeItem(
                "refresh_token"
            );

            window.location.href = "/login";

            return Promise.reject(
                refreshError
            );
        }
    }
);

export default api;
