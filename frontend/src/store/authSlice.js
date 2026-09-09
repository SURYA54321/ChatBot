import { createSlice } from "@reduxjs/toolkit";

const accessToken = localStorage.getItem("access_token");
const refreshToken = localStorage.getItem("refresh_token");

const initialState = {
    accessToken,
    refreshToken,
    isAuthenticated: Boolean(accessToken),
};

const authSlice = createSlice({
    name: "auth",
    initialState,

    reducers: {
        setCredentials: (state, action) => {
            const { access, refresh } = action.payload;

            state.accessToken = access;
            state.refreshToken = refresh;
            state.isAuthenticated = true;

            localStorage.setItem(
                "access_token",
                access
            );

            localStorage.setItem(
                "refresh_token",
                refresh
            );
        },

        logout: (state) => {
            state.accessToken = null;
            state.refreshToken = null;
            state.isAuthenticated = false;

            localStorage.removeItem("access_token");
            localStorage.removeItem("refresh_token");
        },
    },
});

export const {
    setCredentials,
    logout,
} = authSlice.actions;

export default authSlice.reducer;