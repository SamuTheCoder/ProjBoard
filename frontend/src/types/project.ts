export type ProjectCreate = {
    project_name: string;
    project_description: string | null;
};

export type ProjectResponse = {
    project_id: number;
    project_name: string;
    project_description: string | null;
    owner_id: number;
    created_at: string;
    updated_at: string | null;
    member_count: number;
};
