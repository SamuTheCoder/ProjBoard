import axios from "axios";

export function getApiErrorMessage(error: unknown): string {
    if (!axios.isAxiosError(error)) {
        return "Something went wrong.";
    }

    if (!error.response) {
        return "Unable to connect to the server.";
    }

    const data = error.response.data;

    // FastAPI HTTPException
    if (typeof data?.detail === "string") {
        return data.detail;
    }

    // FastAPI/Pydantic validation errors
    if (Array.isArray(data?.detail)) {
        return data.detail.map((error) => error.msg).join(", ");
    }

    return "Something went wrong.";
}
