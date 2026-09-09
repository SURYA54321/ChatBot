import { useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";

import { loginUser } from "../api/authApi";
import { setCredentials } from "../store/authSlice";

function Login() {
    const dispatch = useDispatch();
    const navigate = useNavigate();

    const [username, setUsername] =
        useState("");

    const [password, setPassword] =
        useState("");

    const [loading, setLoading] =
        useState(false);

    const handleSubmit = async (event) => {
        event.preventDefault();

        try {
            setLoading(true);

            const data = await loginUser(
                username,
                password
            );

            dispatch(
                setCredentials(data)
            );

            toast.success("Login successful");

            navigate("/chat");
        } catch (error) {
            toast.error(
                error.response?.data?.detail ||
                "Login failed"
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h1>Login</h1>

            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(event) =>
                        setUsername(
                            event.target.value
                        )
                    }
                />

                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(event) =>
                        setPassword(
                            event.target.value
                        )
                    }
                />

                <button
                    type="submit"
                    disabled={loading}
                >
                    {loading
                        ? "Logging in..."
                        : "Login"}
                </button>
            </form>
        </div>
    );
}

export default Login;