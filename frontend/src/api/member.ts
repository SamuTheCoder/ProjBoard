import { api } from "./client";

import type {
    ProjectMemberCreate,
    ProjectMemberResponse,
} from "../types/member";

export async function getProjectMembers(
    projectId: number,
): Promise<ProjectMemberResponse[]> {
    const response = await api.get<ProjectMemberResponse[]>(
        `/projects/${projectId}/members`,
    );

    return response.data;
}

export async function addProjectMember(
    projectId: number,
    data: ProjectMemberCreate,
): Promise<void> {
    await api.post(`/projects/${projectId}/members`, data);
}

export async function removeProjectMember(
    projectId: number,
    userId: number,
): Promise<void> {
    await api.delete(`/projects/${projectId}/members/${userId}`);
}

export async function transferProjectOwnership(
    projectId: number,
    newOwnerId: number,
): Promise<void> {
    await api.patch(`/projects/${projectId}/members/${newOwnerId}`);
}
