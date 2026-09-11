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

            // >>> Registration errors come back as field-level
            // objects (e.g. {"username": ["This username is already
            // taken."]} or {"password": ["This password is too
            // common."]}), not a flat "detail" string like login
            // errors. Flatten whatever comes back into one message.
            const message = data
                ? Object.values(data).flat().join(" ")
                : "Registration failed";

            toast.error(message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <h1>Register</h1>

            <form onSubmit={handleSubmit}>
                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(event) =>
                        setUsername(event.target.value)
                    }
                />

                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(event) =>
                        setPassword(event.target.value)
                    }
                />

                <button type="submit" disabled={loading}>
                    {loading ? "Creating account..." : "Register"}
                </button>
            </form>

            <p>
                Already have an account? <Link to="/login">Login</Link>
            </p>
        </div>
    );
}

export default Register;