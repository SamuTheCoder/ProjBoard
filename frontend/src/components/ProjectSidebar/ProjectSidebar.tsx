import {
    CalendarDays,
    LayoutDashboard,
    ListTodo,
    Settings,
    Users,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import "./ProjectSidebar.css";

export type ProjectSection =
    | "dashboard"
    | "tasks"
    | "calendar"
    | "members"
    | "settings";

type ProjectSidebarProps = {
    activeSection: ProjectSection;

    onSectionChange: (section: ProjectSection) => void;
};

export function ProjectSidebar({
    activeSection,
    onSectionChange,
}: ProjectSidebarProps) {
    const navigate = useNavigate();

    const sections = [
        {
            key: "dashboard" as const,
            label: "Dashboard",
            icon: LayoutDashboard,
        },
        {
            key: "tasks" as const,
            label: "Tasks",
            icon: ListTodo,
        },
        {
            key: "calendar" as const,
            label: "Calendar",
            icon: CalendarDays,
        },
        {
            key: "members" as const,
            label: "Members",
            icon: Users,
        },
        {
            key: "settings" as const,
            label: "Settings",
            icon: Settings,
        },
    ];

    return (
        <aside className="project-sidebar">
            <button
                className="back-projects"
                onClick={() => navigate("/projects")}
            >
                ← Back to Projects
            </button>

            <nav className="project-sidebar-nav">
                {sections.map(({ key, label, icon: Icon }) => (
                    <button
                        key={key}
                        className={
                            activeSection === key
                                ? "sidebar-item active"
                                : "sidebar-item"
                        }
                        onClick={() => onSectionChange(key)}
                    >
                        <Icon size={18} />

                        {label}
                    </button>
                ))}
            </nav>
        </aside>
    );
}
