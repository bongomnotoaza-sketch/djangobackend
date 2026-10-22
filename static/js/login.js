import { loginUser } from "./api/authentication.js";


const loginForm = document.getElementById(
    "login-form"
);


loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const username =
        document.getElementById("username").value;

    const password =
        document.getElementById("password").value;

    try {
        const result = await loginUser(
            username,
            password
        );

        console.log("Login successful:", result);

    } catch (error) {
        console.error("Login failed:", error.message);
    }
});