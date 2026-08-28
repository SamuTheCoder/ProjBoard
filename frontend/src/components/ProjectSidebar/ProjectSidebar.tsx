import { useNavigate } from "react-router-dom";

import "./ProjectSidebar.css";

export type ProjectSection = "dashboard" | "tasks" | "members" | "settings";

type ProjectSidebarProps = {
    activeSection: ProjectSection;

    onSectionChange: (section: ProjectSection) => void;
};

export function ProjectSidebar({
    activeSection,
    onSectionChange,
}: ProjectSidebarProps) {
    const navigate = useNavigate();

    const sections: {
        key: ProjectSection;
        label: string;
    }[] = [
        {
            key: "dashboard",
            label: "Dashboard",
        },
        {
            key: "tasks",
            label: "Tasks",
        },
        {
            key: "members",
            label: "Members",
        },
        {
            key: "settings",
            label: "Settings",
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
                {sections.map((section) => (
                    <button
                        key={section.key}
                        className={
                            activeSection === section.key
                                ? "sidebar-item active"
                                : "sidebar-item"
                        }
                        onClick={() => onSectionChange(section.key)}
                    >
                        {section.label}
                    </button>
                ))}
            </nav>
        </aside>
    );
}
