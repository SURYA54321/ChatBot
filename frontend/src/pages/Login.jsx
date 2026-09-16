import { useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate, Link } from "react-router-dom";
import toast from "react-hot-toast";

import { loginUser } from "../api/authApi";
import { setCredentials } from "../store/authSlice";

function Login() {
    const dispatch = useDispatch();
    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (event) => {
        event.preventDefault();

        try {
            setLoading(true);

            const data = await loginUser(username, password);

            dispatch(setCredentials(data));

            toast.success("Login successful");

            navigate("/chat");
        } catch (error) {
            toast.error(
                error.response?.data?.detail || "Login failed"
            );
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-page">
            <aside className="login-brand">
                <div className="login-brand__content">
                    <span className="login-brand__mark">Chatbot</span>
                    <p className="login-brand__line">
                        Every conversation, kept in one place.
                    </p>
                </div>
            </aside>

            <main className="login-panel">
                <form className="login-form" onSubmit={handleSubmit} noValidate>
                    <div className="login-form__head">
                        <h1>Welcome back</h1>
                        <p>Sign in to pick up where you left off.</p>
                    </div>

                    <div className="field">
                        <input
                            id="username"
                            type="text"
                            placeholder=" "
                            value={username}
                            onChange={(event) => setUsername(event.target.value)}
                            autoComplete="username"
                        />
                        <label htmlFor="username">Username</label>
                    </div>

                    <div className="field">
                        <input
                            id="password"
                            type="password"
                            placeholder=" "
                            value={password}
                            onChange={(event) => setPassword(event.target.value)}
                            autoComplete="current-password"
                        />
                        <label htmlFor="password">Password</label>
                    </div>

                    <button type="submit" className="login-submit" disabled={loading}>
                        {loading ? "Logging in…" : "Log in"}
                    </button>

                    <p className="login-form__foot">
                        Don't have an account? <Link to="/register">Register</Link>
                    </p>
                </form>
            </main>
        </div>
    );
}

export default Login;