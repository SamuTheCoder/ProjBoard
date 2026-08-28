import { useEffect, useState } from "react";

import type {
    ReviewStatus,
    TaskResponse,
    TaskStatus,
    TaskUpdate,
} from "../../types/task";

import type { ProjectMemberResponse } from "../../types/member";

import { getApiErrorMessage } from "../../api/errors";

import "./TaskDetailsPanel.css";

type TaskDetailsPanelProps = {
    task: TaskResponse;

    members: ProjectMemberResponse[];

    currentUserId: number;
    ownerId: number;

    isClosing?: boolean;
    onClose: () => void;
    onError: (message: string) => void;

    onUpdate: (data: TaskUpdate) => Promise<void>;
};

const statuses: TaskStatus[] = [
    "backlog",
    "ready",
    "in_progress",
    "to_review",
    "done",
];

function statusLabel(status: TaskStatus): string {
    const labels: Record<TaskStatus, string> = {
        backlog: "Backlog",
        ready: "Ready",
        in_progress: "In Progress",
        to_review: "To Review",
        done: "Done",
    };

    return labels[status];
}

function formatDate(value: string | null | undefined) {
    if (!value) return "-";

    return new Date(value).toLocaleString();
}

function toDateTimeInput(value: string | null) {
    if (!value) return "";

    const date = new Date(value);

    const offset = date.getTimezoneOffset() * 60000;

    return new Date(date.getTime() - offset).toISOString().slice(0, 16);
}

export function TaskDetailsPanel({
    task,
    members,
    currentUserId,
    ownerId,
    isClosing = false,
    onClose,
    onError,
    onUpdate,
}: TaskDetailsPanelProps) {
    const [editing, setEditing] = useState(false);

    const [name, setName] = useState(task.task_name);

    const [description, setDescription] = useState(task.task_description ?? "");

    const [priority, setPriority] = useState(task.priority);

    const [deadline, setDeadline] = useState(
        toDateTimeInput(task.task_deadline),
    );

    const [assigneeId, setAssigneeId] = useState(
        task.assignee_id?.toString() ?? "",
    );

    const [reviewerId, setReviewerId] = useState(
        task.reviewer_id?.toString() ?? "",
    );

    const [status, setStatus] = useState<TaskStatus>(task.status);

    const [reviewStatus, setReviewStatus] = useState<ReviewStatus | "">(
        task.review_status ?? "",
    );

    useEffect(() => {
        setName(task.task_name);

        setDescription(task.task_description ?? "");

        setPriority(task.priority);

        setDeadline(toDateTimeInput(task.task_deadline));

        setAssigneeId(task.assignee_id?.toString() ?? "");

        setReviewerId(task.reviewer_id?.toString() ?? "");

        setStatus(task.status);

        setReviewStatus(task.review_status ?? "");

        setEditing(false);
    }, [task]);

    const isOwner = currentUserId === ownerId;

    const immutable = task.status === "done";

    const canEditCore =
        !immutable && (isOwner || currentUserId === task.created_by);

    const canChangeStatus =
        !immutable && (isOwner || currentUserId === task.assignee_id);

    const canReview =
        !immutable && (isOwner || currentUserId === task.reviewer_id);

    const canEdit = canEditCore || canChangeStatus || canReview;

    function memberName(userId: number | null) {
        if (!userId) return null;

        const member = members.find((member) => member.user_id === userId);

        if (!member) return null;

        return `${member.first_name} ${member.last_name}`;
    }

    async function handleSave() {
        const update: TaskUpdate = {};

        if (canEditCore) {
            if (name !== task.task_name) {
                update.task_name = name;
            }

            const oldDescription = task.task_description ?? "";

            if (description !== oldDescription) {
                update.task_description = description || null;
            }

            if (priority !== task.priority) {
                update.priority = priority;
            }

            const newAssignee = assigneeId ? Number(assigneeId) : null;

            if (newAssignee !== task.assignee_id) {
                update.assignee_id = newAssignee;
            }

            const newReviewer = reviewerId ? Number(reviewerId) : null;

            if (newReviewer !== task.reviewer_id) {
                update.reviewer_id = newReviewer;
            }

            const oldDeadline = toDateTimeInput(task.task_deadline);

            if (deadline !== oldDeadline) {
                update.task_deadline = deadline
                    ? new Date(deadline).toISOString()
                    : null;
            }
        }

        if (canChangeStatus && status !== task.status) {
            update.status = status;
        }

        if (canReview) {
            const nextReviewStatus = reviewStatus || null;

            if (nextReviewStatus !== task.review_status) {
                update.review_status = nextReviewStatus;
            }
        }

        if (Object.keys(update).length === 0) {
            setEditing(false);
            return;
        }

        try {
            await onUpdate(update);

            setEditing(false);
        } catch (error) {
            onError(getApiErrorMessage(error));
        }
    }

    return (
        <aside className={`task-details-panel ${isClosing ? "closing" : ""}`}>
            <div className="task-details-header">
                <button
                    type="button"
                    className="task-details-close"
                    onClick={onClose}
                >
                    ×
                </button>
            </div>

            {!editing ? (
                <>
                    <div className="task-details-title">
                        <h2>{task.task_name}</h2>

                        {canEdit && (
                            <button
                                type="button"
                                className="task-edit-button"
                                onClick={() => setEditing(true)}
                            >
                                Edit
                            </button>
                        )}
                    </div>

                    <div className="task-details-status">
                        {statusLabel(task.status)}
                    </div>

                    <div className="task-details-section">
                        <h4>Description</h4>

                        <p>
                            {task.task_description ||
                                "No description provided."}
                        </p>
                    </div>

                    <div className="task-details-section">
                        <div className="task-detail-row">
                            <span>Priority</span>

                            <strong>{task.priority}</strong>
                        </div>

                        <div className="task-detail-row">
                            <span>Due date</span>

                            <strong>{formatDate(task.task_deadline)}</strong>
                        </div>
                    </div>

                    <div className="task-details-section">
                        <div className="task-detail-row">
                            <span>Creator</span>

                            <strong>
                                {memberName(task.created_by) || "Unknown"}
                            </strong>
                        </div>

                        <div className="task-detail-row">
                            <span>Assignee</span>

                            <strong>
                                {memberName(task.assignee_id) || "Unassigned"}
                            </strong>
                        </div>

                        <div className="task-detail-row">
                            <span>Reviewer</span>

                            <strong>
                                {memberName(task.reviewer_id) || "None"}
                            </strong>
                        </div>

                        <div className="task-detail-row">
                            <span>Review status</span>

                            <strong>{task.review_status || "None"}</strong>
                        </div>
                    </div>

                    <div className="task-details-section">
                        <div className="task-detail-row">
                            <span>Created</span>

                            <strong>{formatDate(task.created_at)}</strong>
                        </div>

                        <div className="task-detail-row">
                            <span>Updated</span>

                            <strong>{formatDate(task.updated_at)}</strong>
                        </div>
                    </div>

                    {immutable && (
                        <p className="task-immutable-message">
                            Done tasks cannot be edited.
                        </p>
                    )}
                </>
            ) : (
                <div className="task-edit-form">
                    {canEditCore && (
                        <>
                            <label>Task name</label>

                            <input
                                value={name}
                                onChange={(event) =>
                                    setName(event.target.value)
                                }
                            />

                            <label>Description</label>

                            <textarea
                                value={description}
                                onChange={(event) =>
                                    setDescription(event.target.value)
                                }
                            />

                            <label>Priority</label>

                            <select
                                value={priority}
                                onChange={(event) =>
                                    setPriority(Number(event.target.value))
                                }
                            >
                                {[1, 2, 3, 4, 5].map((value) => (
                                    <option key={value} value={value}>
                                        {value}
                                    </option>
                                ))}
                            </select>

                            <label>Deadline</label>

                            <input
                                type="datetime-local"
                                value={deadline}
                                onChange={(event) =>
                                    setDeadline(event.target.value)
                                }
                            />

                            <label>Assignee</label>

                            <select
                                value={assigneeId}
                                onChange={(event) =>
                                    setAssigneeId(event.target.value)
                                }
                            >
                                <option value="">Unassigned</option>

                                {members.map((member) => (
                                    <option
                                        key={member.user_id}
                                        value={member.user_id}
                                    >
                                        {member.first_name} {member.last_name}
                                    </option>
                                ))}
                            </select>

                            <label>Reviewer</label>

                            <select
                                value={reviewerId}
                                onChange={(event) =>
                                    setReviewerId(event.target.value)
                                }
                            >
                                <option value="">None</option>

                                {members.map((member) => (
                                    <option
                                        key={member.user_id}
                                        value={member.user_id}
                                    >
                                        {member.first_name} {member.last_name}
                                    </option>
                                ))}
                            </select>
                        </>
                    )}

                    {canChangeStatus && (
                        <>
                            <label>Status</label>

                            <select
                                value={status}
                                onChange={(event) =>
                                    setStatus(event.target.value as TaskStatus)
                                }
                            >
                                {statuses.map((value) => (
                                    <option key={value} value={value}>
                                        {statusLabel(value)}
                                    </option>
                                ))}
                            </select>
                        </>
                    )}

                    {canReview && (
                        <>
                            <label>Review status</label>

                            <select
                                value={reviewStatus}
                                onChange={(event) =>
                                    setReviewStatus(
                                        event.target.value as ReviewStatus | "",
                                    )
                                }
                            >
                                <option value="">None</option>

                                <option value="pending">Pending</option>

                                <option value="approved">Approved</option>

                                <option value="rejected">Rejected</option>
                            </select>
                        </>
                    )}

                    <div className="task-edit-actions">
                        <button type="button" onClick={() => setEditing(false)}>
                            Cancel
                        </button>

                        <button
                            type="button"
                            className="primary"
                            onClick={handleSave}
                        >
                            Save
                        </button>
                    </div>
                </div>
            )}
        </aside>
    );
}
