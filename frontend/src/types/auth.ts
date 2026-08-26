export type RegisterRequest = {
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    password: string;
};

export type LoginRequest = {
    username: string;
    password: string;
};

export type UserResponse = {
    user_id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    created_at: string;
};

export type LoginResponse = {
    access_token: string;
    token_type: string;
};
