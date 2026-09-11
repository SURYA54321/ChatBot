import api from "./axios";

export const loginUser = async (username, password) => {
    const response = await api.post("/auth/token/", {
        username,
        password,
    });

    return response.data;
};

// >>> NEW
export const registerUser = async (username, password) => {
    const response = await api.post("/auth/register/", {
        username,
        password,
    });

    return response.data;
};

export const refreshToken = async (refresh) => {
    const response = await api.post("/auth/token/refresh/", {
        refresh,
    });

    return response.data;
};