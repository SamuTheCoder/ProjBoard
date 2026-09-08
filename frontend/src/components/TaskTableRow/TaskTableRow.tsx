import { FolderKanban } from "lucide-react";

import type { TaskStatus } from "../../types/task";

import "./TaskTableRow.css";

export type TaskRole = "assignee" | "creator" | "reviewer";

type TaskTableRowProps = {
    name: string;
    description?: string | null;

    projectName: string;

    role: TaskRole;

    priority: number;
    status: TaskStatus;

    dueDate?: string | null;

    onClick?: () => void;
};

function statusLabel(status: TaskStatus) {
    const labels: Record<TaskStatus, string> = {
        backlog: "Backlog",
        ready: "Ready",
        in_progress: "In Progress",
        to_review: "To Review",
        done: "Done",
    };

    return labels[status];
}

function roleLabel(role: TaskRole) {
    const labels: Record<TaskRole, string> = {
        assignee: "Assignee",
        creator: "Creator",
        reviewer: "Reviewer",
    };

    return labels[role];
}

function formatDate(date?: string | null) {
    if (!date) return "No deadline";

    return new Date(date).toLocaleDateString();
}

export function TaskTableRow({
    name,
    description,
    projectName,
    role,
    priority,
    status,
    dueDate,
    onClick,
}: TaskTableRowProps) {
    return (
        <button type="button" className="my-task-row" onClick={onClick}>
            <div className="my-task-main">
                <strong>{name}</strong>

                {description && <span>{description}</span>}
            </div>

            <div className="my-task-project">
                <FolderKanban size={17} />
                <span>{projectName}</span>
            </div>

            <div>
                <span className={`my-task-role role-${role}`}>
                    {roleLabel(role)}
                </span>
            </div>

            <div>
                <span className={`my-task-priority priority-${priority}`}>
                    P{priority}
                </span>
            </div>

            <div>
                <span className={`my-task-status status-${status}`}>
                    {statusLabel(status)}
                </span>
            </div>

            <div className="my-task-date">{formatDate(dueDate)}</div>
        </button>
    );
}
