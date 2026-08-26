import { api } from "./client";
import type { UserResponse } from "../types/auth";

export async function getCurrentUser(): Promise<UserResponse> {
    const response = await api.get("/users/me");

    return response.data;
}
