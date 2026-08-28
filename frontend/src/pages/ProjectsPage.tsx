import { Navbar } from "../components/Navbar";
import { ProjectCard } from "../components/ProjectCard";
import { Button } from "../components/Button";
import { useEffect, useState } from "react";
import { getCurrentUser } from "../api/user";
import "./ProjectsPage.css";
import type { UserResponse } from "../types/auth";
import { getProjects } from "../api/project";
import type { ProjectResponse } from "../types/project";
import { CreateProjectModal } from "../components/CreateProjectModal";
import { useNavigate } from "react-router-dom";
import { ErrorToast } from "../components/ErrorToast/ErrorToast";

export function ProjectsPage() {
    const [projects, setProjects] = useState<ProjectResponse[]>([]);

    const [user, setUser] = useState<UserResponse | null>(null);
    const [isCreateOpen, setIsCreateOpen] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        async function loadUser() {
            const currentUser = await getCurrentUser();
            setUser(currentUser);
        }

        loadUser();

        async function loadProjects() {
            const data = await getProjects();
            setProjects(data);
        }

        loadProjects();
    }, []);

    return (
        <div className="projects-page">
            <Navbar />

            <main className="projects-content">
                <section className="projects-welcome">
                    <h1>Welcome back{user ? `, ${user.first_name}` : ""}</h1>
                    <p>Here are the projects you're involved in.</p>
                </section>

                <section className="projects-section">
                    <div className="projects-header">
                        <h2>Your Projects</h2>

                        <div className="new-project-button">
                            <Button
                                type="button"
                                onClick={() => setIsCreateOpen(true)}
                            >
                                + New Project
                            </Button>
                        </div>
                    </div>

                    <div className="projects-grid">
                        {projects.map((project) => (
                            <ProjectCard
                                key={project.project_id}
                                name={project.project_name}
                                description={project.project_description}
                                memberCount={project.member_count}
                                onClick={() =>
                                    navigate(`/projects/${project.project_id}`)
                                }
                            />
                        ))}
                    </div>
                </section>
            </main>

            <CreateProjectModal
                isOpen={isCreateOpen}
                onClose={() => setIsCreateOpen(false)}
                onCreated={(project: ProjectResponse) => {
                    setProjects((current) => [...current, project]);
                    setIsCreateOpen(false);
                }}
            />
        </div>
    );
}
