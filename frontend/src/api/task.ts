import { api } from "./client";

import type { TaskCreate, TaskUpdate, TaskResponse } from "../types/task";

export async function getProjectTasks(
    projectId: number,
): Promise<TaskResponse[]> {
    const response = await api.get<TaskResponse[]>(
        `/projects/${projectId}/tasks`,
    );

    return response.data;
}

export async function createTask(
    projectId: number,
    data: TaskCreate,
): Promise<TaskResponse> {
    const response = await api.post<TaskResponse>(
        `/projects/${projectId}/tasks`,
        data,
    );

    return response.data;
}

export async function updateTask(
    projectId: number,
    taskId: number,
    data: TaskUpdate,
): Promise<TaskResponse> {
    const response = await api.patch<TaskResponse>(
        `/projects/${projectId}/tasks/${taskId}`,
        data,
    );

    return response.data;
}
