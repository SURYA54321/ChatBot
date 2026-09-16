import { useState } from "react";
import { useDispatch } from "react-redux";
import { useNavigate, Link } from "react-router-dom";
import toast from "react-hot-toast";

import { registerUser } from "../api/authApi";
import { setCredentials } from "../store/authSlice";

function Register() {
    const dispatch = useDispatch();
    const navigate = useNavigate();

    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (event) => {
        event.preventDefault();

        try {
            setLoading(true);

            const data = await registerUser(username, password);

            dispatch(setCredentials(data));

            toast.success("Account created");

            navigate("/chat");
        } catch (error) {
            const data = error.response?.data;

            const message = data
                ? Object.values(data).flat().join(" ")
                : "Registration failed";

            toast.error(message);
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
                        Start a conversation worth keeping.
                    </p>
                </div>
            </aside>

            <main className="login-panel">
                <form className="login-form" onSubmit={handleSubmit} noValidate>
                    <div className="login-form__head">
                        <h1>Create your account</h1>
                        <p>Takes a few seconds — no email required.</p>
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
                            autoComplete="new-password"
                        />
                        <label htmlFor="password">Password</label>
                    </div>

                    <button type="submit" className="login-submit" disabled={loading}>
                        {loading ? "Creating account…" : "Create account"}
                    </button>

                    <p className="login-form__foot">
                        Already have an account? <Link to="/login">Log in</Link>
                    </p>
                </form>
            </main>
        </div>
    );
}

export default Register;