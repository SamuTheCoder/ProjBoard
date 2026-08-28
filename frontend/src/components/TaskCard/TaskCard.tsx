import "./TaskCard.css";

type TaskCardProps = {
    name: string;
    priority: number;
    assigneeInitials?: string;
    onClick?: () => void;
};

export function TaskCard({
    name,
    priority,
    assigneeInitials,
    onClick,
}: TaskCardProps) {
    return (
        <div className="task-card" onClick={onClick}>
            <h4>{name}</h4>

            <div className="task-card-footer">
                <span className={`task-priority priority-${priority}`}>
                    P{priority}
                </span>

                {assigneeInitials && (
                    <span className="task-assignee">{assigneeInitials}</span>
                )}
            </div>
        </div>
    );
}
