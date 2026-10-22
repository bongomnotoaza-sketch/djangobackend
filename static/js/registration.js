import { registerUser } from "./api/authentication.js";


const registrationForm = document.getElementById(
    "registration-form"
);


registrationForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const userData = {
        username: document.getElementById("username").value,
        password: document.getElementById("password").value,
        first_name: document.getElementById("first_name").value,
        last_name: document.getElementById("last_name").value,
        email: document.getElementById("email").value,
        phone: document.getElementById("phone").value,
        date_of_birth: document.getElementById("date_of_birth").value,
        country: document.getElementById("country").value,
        city: document.getElementById("city").value,
        current_activity: document.getElementById("current_activity").value,
    };

    try {
        const result = await registerUser(userData);

        console.log("Registration successful:", result);

    } catch (error) {
        console.error("Registration failed:", error.message);
    }
});