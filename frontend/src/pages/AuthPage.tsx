import { useState } from "react";
import { Brand } from "../components/Brand";
import { FormField } from "../components/FormField";
import { Button } from "../components/Button";
import { login, register } from "../api/auth";
import { getApiErrorMessage } from "../api/errors";
import { useNavigate } from "react-router-dom";
import "./AuthPage.css";
import { ErrorToast } from "../components/ErrorToast/ErrorToast";

type AuthMode = "login" | "register";

export function AuthPage() {
    const [formData, setFormData] = useState({
        username: "",
        email: "",
        first_name: "",
        last_name: "",
        password: "",
        confirmPassword: "",
    });

    const [mode, setMode] = useState<AuthMode>("login");

    const isLogin = mode === "login";
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

    const navigate = useNavigate();

    function handleChange(event: React.ChangeEvent<HTMLInputElement>) {
        setFormData({
            ...formData,
            [event.target.name]: event.target.value,
        });
    }

    function changeMode(mode: AuthMode) {
        setMode(mode);
        setError("");
        setSuccess("");
    }

    async function handleSubmit(event: React.FormEvent) {
        event.preventDefault();
        setError("");

        if (!isLogin && formData.password !== formData.confirmPassword) {
            setError("Passwords do not match.");
            return;
        }

        try {
            if (isLogin) {
                const response = await login({
                    username: formData.username,
                    password: formData.password,
                });

                localStorage.setItem("token", response.access_token);

                setSuccess("Login successful.");
                navigate("/projects");
            } else {
                await register({
                    username: formData.username,
                    email: formData.email,
                    first_name: formData.first_name,
                    last_name: formData.last_name,
                    password: formData.password,
                });

                setSuccess("Account created successfully. You can now log in.");
                changeMode("login");
            }
        } catch (error) {
            setError(getApiErrorMessage(error));
        }
    }

    return (
        <main className="auth-page">
            <ErrorToast message={error} onClose={() => setError("")} />
            <section
                className={`auth-left ${isLogin ? "login-mode" : "register-mode"}`}
            >
                <Brand size="md" />

                <div className="auth-content">
                    <div className="auth-heading">
                        <h1>
                            {isLogin ? "Welcome back" : "Create an account"}
                        </h1>
                        <p>
                            {isLogin
                                ? "Log in to your account to continue managing your projects."
                                : "Create your account and start organizing your projects."}
                        </p>
                    </div>

                    <div className="auth-tabs">
                        <button
                            className={isLogin ? "active" : ""}
                            onClick={() => changeMode("login")}
                        >
                            Log in
                        </button>

                        <button
                            className={!isLogin ? "active" : ""}
                            onClick={() => changeMode("register")}
                        >
                            Register
                        </button>
                    </div>

                    <form className="auth-form" onSubmit={handleSubmit}>
                        {isLogin ? (
                            <>
                                <FormField
                                    label="Username"
                                    name="username"
                                    type="text"
                                    placeholder="Choose a username"
                                    value={formData.username}
                                    onChange={handleChange}
                                />

                                <FormField
                                    label="Password"
                                    name="password"
                                    type="password"
                                    placeholder="Enter your password"
                                    value={formData.password}
                                    onChange={handleChange}
                                />
                            </>
                        ) : (
                            <>
                                <FormField
                                    label="Username"
                                    name="username"
                                    type="text"
                                    placeholder="Choose a username"
                                    value={formData.username}
                                    onChange={handleChange}
                                />

                                <FormField
                                    label="Email"
                                    name="email"
                                    type="email"
                                    placeholder="you@example.com"
                                    value={formData.email}
                                    onChange={handleChange}
                                />

                                <FormField
                                    label="First name"
                                    name="first_name"
                                    type="text"
                                    placeholder="Enter your first name"
                                    value={formData.first_name}
                                    onChange={handleChange}
                                />

                                <FormField
                                    label="Last name"
                                    name="last_name"
                                    type="text"
                                    placeholder="Enter your last name"
                                    value={formData.last_name}
                                    onChange={handleChange}
                                />

                                <FormField
                                    label="Password"
                                    name="password"
                                    type="password"
                                    placeholder="Choose a password"
                                    value={formData.password}
                                    onChange={handleChange}
                                />

                                <FormField
                                    label="Confirm password"
                                    name="confirmPassword"
                                    type="password"
                                    placeholder="Repeat your password"
                                    value={formData.confirmPassword}
                                    onChange={handleChange}
                                />
                            </>
                        )}
                        <p className="form-success">{success}</p>
                        <Button type="submit">
                            {isLogin ? "Log in" : "Register"}
                        </Button>
                    </form>
                </div>
            </section>

            <section className="auth-right">
                <div className="auth-right-content">
                    <img
                        src="/projboard-icon.svg"
                        alt=""
                        className="auth-right-logo"
                    />

                    <h2>
                        Projects organized.
                        <br />
                        Teams aligned. Goals achieved.
                    </h2>

                    <p>
                        ProjBoard helps you manage projects, assign tasks, and
                        track progress in one simple workspace.
                    </p>
                </div>
            </section>
        </main>
    );
}
