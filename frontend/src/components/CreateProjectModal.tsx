import { useState } from "react";
import { createProject } from "../api/project";
import type { ProjectResponse } from "../types/project";
import { Button } from "./Button";
import { FormField } from "./FormField";
import "./CreateProjectModal.css";
import { getApiErrorMessage } from "../api/errors";

type CreateProjectModalProps = {
    isOpen: boolean;
    onClose: () => void;
    onCreated: (project: ProjectResponse) => void;
};

export function CreateProjectModal({
    isOpen,
    onClose,
    onCreated,
}: CreateProjectModalProps) {
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");
    const [error, setError] = useState("");

    if (!isOpen) return null;

    async function handleSubmit(event: React.SubmitEvent<HTMLFormElement>) {
        event.preventDefault();

        setError("");

        try {
            const project = await createProject({
                project_name: name,
                project_description: description || null,
            });

            onCreated(project);

            setName("");
            setDescription("");
        } catch (error) {
            setError(getApiErrorMessage(error));
        }
    }

    function handleClose() {
        setError("");
        onClose();
    }

    return (
        <div className="modal-backdrop">
            <div className="create-project-modal">
                <h2>Create new project</h2>

                <form onSubmit={handleSubmit}>
                    <FormField
                        label="Project name"
                        name="project_name"
                        value={name}
                        onChange={(event) => setName(event.target.value)}
                        placeholder="Enter project name"
                        required
                    />

                    <div className="project-description-field">
                        <label htmlFor="project_description">Description</label>

                        <textarea
                            id="project_description"
                            value={description}
                            onChange={(event) =>
                                setDescription(event.target.value)
                            }
                            placeholder="Describe your project"
                            maxLength={255}
                        />
                    </div>

                    {error && <p className="form-error">{error}</p>}

                    <div className="modal-actions">
                        <Button type="button" onClick={handleClose}>
                            Cancel
                        </Button>

                        <Button type="submit">Create Project</Button>
                    </div>
                </form>
            </div>
        </div>
    );
}
