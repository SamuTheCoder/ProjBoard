import axios from "axios";

export const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL,
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem("token");

    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
});

api.interceptors.response.use(
    (response) => response,

    (error) => {
        if (
            error.response?.status === 401 &&
            error.config?.url !== "/auth/login"
        ) {
            localStorage.removeItem("token");
            window.location.href = "/";
        }

        return Promise.reject(error);
    },
);
