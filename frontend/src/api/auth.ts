import { api } from "./client";

import type {
    RegisterRequest,
    LoginRequest,
    UserResponse,
    LoginResponse,
} from "../types/auth";

export async function register(data: RegisterRequest): Promise<UserResponse> {
    const response = await api.post<UserResponse>("/auth/register", data);

    return response.data;
}

export async function login(data: LoginRequest): Promise<LoginResponse> {
    const formData = new URLSearchParams();

    formData.append("username", data.username);
    formData.append("password", data.password);

    const response = await api.post<LoginResponse>("/auth/login", formData, {
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
    });

    return response.data;
}
