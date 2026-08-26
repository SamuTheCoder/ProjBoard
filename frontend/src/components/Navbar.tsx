import { NavLink, useNavigate } from "react-router-dom";
import { Brand } from "./Brand";
import "./Navbar.css";

export function Navbar() {
    const navigate = useNavigate();

    function handleLogout() {
        localStorage.removeItem("token");
        navigate("/");
    }

    return (
        <nav className="navbar">
            <Brand size="md" />

            <div className="navbar-links">
                <NavLink
                    to="/projects"
                    className={({ isActive }) => (isActive ? "active" : "")}
                >
                    Projects
                </NavLink>

                <button type="button">My Tasks</button>
                <button type="button">Activity</button>
            </div>

            <div className="navbar-user">
                <NavLink
                    to="/profile"
                    className={({ isActive }) => (isActive ? "active" : "")}
                >
                    Profile
                </NavLink>

                <button type="button" onClick={handleLogout}>
                    Logout
                </button>
            </div>
        </nav>
    );
}
