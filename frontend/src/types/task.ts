export type TaskStatus =
    | "backlog"
    | "ready"
    | "in_progress"
    | "to_review"
    | "done";

export type ReviewStatus = "pending" | "approved" | "rejected";

export type TaskCreate = {
    task_name: string;
    task_description: string | null;

    assignee_id?: number | null;
    reviewer_id?: number | null;

    priority?: number;

    task_deadline?: string | null;
};

export type TaskUpdate = {
    task_name?: string;
    task_description?: string | null;

    assignee_id?: number | null;
    reviewer_id?: number | null;

    priority?: number;

    status?: TaskStatus;
    review_status?: ReviewStatus | null;

    task_deadline?: string | null;
};

export type TaskResponse = {
    task_id: number;
    project_id: number;

    task_name: string;
    task_description: string | null;

    created_by: number;

    created_at: string;
    updated_at: string;

    assignee_id: number | null;
    reviewer_id: number | null;

    priority: number;

    status: TaskStatus;
    review_status: ReviewStatus | null;

    task_deadline: string | null;
};
