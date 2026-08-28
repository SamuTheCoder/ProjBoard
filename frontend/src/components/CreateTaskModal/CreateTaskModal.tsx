import { useState } from "react";

import { Button } from "../Button";
import { FormField } from "../FormField";

import { getApiErrorMessage } from "../../api/errors";

import type { TaskCreate } from "../../types/task";
import type { ProjectMemberResponse } from "../../types/member";

import "./CreateTaskModal.css";

type CreateTaskModalProps = {
    isOpen: boolean;
    members: ProjectMemberResponse[];

    onClose: () => void;

    onSubmit: (data: TaskCreate) => Promise<void>;
};

export function CreateTaskModal({
    isOpen,
    members,
    onClose,
    onSubmit,
}: CreateTaskModalProps) {
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");

    const [priority, setPriority] = useState(3);

    const [deadline, setDeadline] = useState("");

    const [assigneeId, setAssigneeId] = useState("");

    const [reviewerId, setReviewerId] = useState("");

    const [error, setError] = useState("");

    if (!isOpen) return null;

    function resetForm() {
        setName("");
        setDescription("");
        setPriority(3);
        setDeadline("");
        setAssigneeId("");
        setReviewerId("");
        setError("");
    }

    function handleClose() {
        resetForm();
        onClose();
    }

    async function handleSubmit(event: React.SubmitEvent<HTMLFormElement>) {
        event.preventDefault();

        setError("");

        try {
            await onSubmit({
                task_name: name,

                task_description: description || null,

                priority,

                assignee_id: assigneeId ? Number(assigneeId) : null,

                reviewer_id: reviewerId ? Number(reviewerId) : null,

                task_deadline: deadline
                    ? new Date(deadline).toISOString()
                    : null,
            });

            resetForm();
        } catch (error) {
            setError(getApiErrorMessage(error));
        }
    }

    return (
        <div className="modal-backdrop">
            <div className="create-task-modal">
                <h2>Create new task</h2>

                <form onSubmit={handleSubmit}>
                    <FormField
                        label="Task name"
                        name="task_name"
                        value={name}
                        onChange={(event) => setName(event.target.value)}
                        placeholder="Enter task name"
                        required
                    />

                    <div className="task-modal-field">
                        <label>Description</label>

                        <textarea
                            value={description}
                            onChange={(event) =>
                                setDescription(event.target.value)
                            }
                            placeholder="Describe the task"
                        />
                    </div>

                    <div className="task-modal-row">
                        <div className="task-modal-field">
                            <label>Priority</label>

                            <select
                                value={priority}
                                onChange={(event) =>
                                    setPriority(Number(event.target.value))
                                }
                            >
                                <option value={1}>1</option>
                                <option value={2}>2</option>
                                <option value={3}>3</option>
                                <option value={4}>4</option>
                                <option value={5}>5</option>
                            </select>
                        </div>

                        <div className="task-modal-field">
                            <label>Deadline</label>

                            <input
                                type="datetime-local"
                                value={deadline}
                                onChange={(event) =>
                                    setDeadline(event.target.value)
                                }
                            />
                        </div>
                    </div>

                    <div className="task-modal-field">
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
                    </div>

                    <div className="task-modal-field">
                        <label>Reviewer</label>

                        <select
                            value={reviewerId}
                            onChange={(event) =>
                                setReviewerId(event.target.value)
                            }
                        >
                            <option value="">No reviewer</option>

                            {members.map((member) => (
                                <option
                                    key={member.user_id}
                                    value={member.user_id}
                                >
                                    {member.first_name} {member.last_name}
                                </option>
                            ))}
                        </select>
                    </div>

                    {error && <p className="form-error">{error}</p>}

                    <div className="modal-actions">
                        <Button type="button" onClick={handleClose}>
                            Cancel
                        </Button>

                        <Button type="submit">Create Task</Button>
                    </div>
                </form>
            </div>
        </div>
    );
}
