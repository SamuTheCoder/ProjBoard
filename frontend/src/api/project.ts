import { api } from "./client";
import type { ProjectCreate, ProjectResponse } from "../types/project";

export async function getProjects(): Promise<ProjectResponse[]> {
    const response = await api.get<ProjectResponse[]>("/projects");

    return response.data;
}

export async function createProject(
    data: ProjectCreate,
): Promise<ProjectResponse> {
    const response = await api.post<ProjectResponse>("/projects", data);
    return response.data;
}
