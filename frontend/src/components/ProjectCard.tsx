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
            <div className="project-card-icon">📁</div>

            <h3>{name}</h3>

            <p>{description}</p>

            <div className="project-card-footer">
                <span>
                    👥 {memberCount} {memberCount === 1 ? "member" : "members"}
                </span>

                <span className="project-card-arrow">›</span>
            </div>
        </div>
    );
}
