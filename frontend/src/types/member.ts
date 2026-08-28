export type ProjectMemberCreate = {
    username: string;
};

export type ProjectRole = "owner" | "member";

export type ProjectMemberResponse = {
    project_id: number;
    user_id: number;
    role: ProjectRole;
    joined_at: string;

    username: string;
    email: string;
    first_name: string;
    last_name: string;
};
