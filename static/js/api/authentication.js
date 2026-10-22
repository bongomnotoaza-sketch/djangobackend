const AUTH_BASE_URL = "/auth";


async function handleResponse(response) {
    const data = await response.json();

    if (!response.ok) {
        throw new Error(
            data.error || "Authentication request failed."
        );
    }

    return data;
}


export async function registerUser(userData) {
    const response = await fetch(
        `${AUTH_BASE_URL}/register/`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
            },

            credentials: "include",

            body: JSON.stringify(userData),
        }
    );

    return handleResponse(response);
}


export async function loginUser(username, password) {
    const response = await fetch(
        `${AUTH_BASE_URL}/login/`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json",
            },

            credentials: "include",

            body: JSON.stringify({
                username,
                password,
            }),
        }
    );

    return handleResponse(response);
}


export async function verifyEmail(token) {
    const response = await fetch(
        `${AUTH_BASE_URL}/verify-email/?token=${encodeURIComponent(token)}`,
        {
            method: "GET",

            credentials: "include",
        }
    );

    return handleResponse(response);
}