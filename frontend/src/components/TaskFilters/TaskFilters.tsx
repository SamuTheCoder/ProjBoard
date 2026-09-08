import { RotateCcw } from "lucide-react";

import type { ProjectResponse } from "../../types/project";

import "./TaskFilters.css";

export type TaskFilterState = {
    status: string;
    priority: string;
    projectId: string;
    role: string;
};

type TaskFiltersProps = {
    filters: TaskFilterState;

    projects: ProjectResponse[];

    onChange: (filters: TaskFilterState) => void;

    onClear: () => void;
};

export function TaskFilters({
    filters,
    projects,
    onChange,
    onClear,
}: TaskFiltersProps) {
    function updateFilter(field: keyof TaskFilterState, value: string) {
        onChange({
            ...filters,
            [field]: value,
        });
    }

    return (
        <div className="task-filters-bar">
            <select
                value={filters.status}
                onChange={(event) => updateFilter("status", event.target.value)}
            >
                <option value="all">Status</option>

                <option value="backlog">Backlog</option>

                <option value="ready">Ready</option>

                <option value="in_progress">In Progress</option>

                <option value="to_review">To Review</option>

                <option value="done">Done</option>
            </select>

            <select
                value={filters.priority}
                onChange={(event) =>
                    updateFilter("priority", event.target.value)
                }
            >
                <option value="all">Priority</option>

                {[1, 2, 3, 4, 5].map((priority) => (
                    <option key={priority} value={priority}>
                        P{priority}
                    </option>
                ))}
            </select>

            <select
                value={filters.projectId}
                onChange={(event) =>
                    updateFilter("projectId", event.target.value)
                }
            >
                <option value="all">Project</option>

                {projects.map((project) => (
                    <option key={project.project_id} value={project.project_id}>
                        {project.project_name}
                    </option>
                ))}
            </select>

            <select
                value={filters.role}
                onChange={(event) => updateFilter("role", event.target.value)}
            >
                <option value="all">Role</option>

                <option value="assignee">Assignee</option>

                <option value="creator">Creator</option>

                <option value="reviewer">Reviewer</option>
            </select>

            <button
                type="button"
                className="task-filters-clear"
                onClick={onClear}
            >
                <RotateCcw size={16} />
                Clear filters
            </button>
        </div>
    );
}
