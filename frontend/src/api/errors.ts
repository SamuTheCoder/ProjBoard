import axios from "axios";

export function getApiErrorMessage(error: unknown): string {
    if (!axios.isAxiosError(error)) {
        return "Something went wrong.";
    }

    if (!error.response) {
        return "Unable to connect to the server.";
    }

    const { status, data } = error.response;

    if (status === 401) {
        return data.detail ?? "Invalid username or password.";
    }

    if (status === 409) {
        return data.detail ?? "This account already exists.";
    }

    if (status === 422) {
        return "Please check the information you entered.";
    }

    return "Something went wrong.";
}
