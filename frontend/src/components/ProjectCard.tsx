import { FolderKanban, Users, ChevronRight } from "lucide-react";

import "./ProjectCard.css";

type ProjectCardProps = {
    name: string;
    description: string;
    memberCount: number;
    onClick?: () => void;
};

export function ProjectCard({
    name,
    description,
    memberCount,
    onClick,
}: ProjectCardProps) {
    return (
        <div className="project-card" onClick={onClick}>
            <div className="project-card-icon">
                <FolderKanban size={24} />
            </div>

            <h3>{name}</h3>

            <p>{description}</p>

            <div className="project-card-footer">
                <span className="project-card-members">
                    <Users size={18} />
                    {memberCount} {memberCount === 1 ? "member" : "members"}
                </span>

                <ChevronRight className="project-card-arrow" size={20} />
            </div>
        </div>
    );
}
