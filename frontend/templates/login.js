const API_BASE_URL = "https://projet-hebergement.onrender.com";
const loginForm = document.querySelector("#login-form");
const registerForm = document.querySelector("#register-form");
const loginTab = document.querySelector("#login-tab");
const registerTab = document.querySelector("#register-tab");
const authMessage = document.querySelector("#auth-message");

function setAuthMessage(message, isError = false) {
    authMessage.textContent = message;
    authMessage.dataset.state = isError ? "error" : "success";
}

function formatDetail(detail) {
    if (typeof detail === "string") {
        return detail;
    }
    if (!Array.isArray(detail)) {
        return "";
    }

    return detail
        .map((error) => {
            if (typeof error === "string") {
                return error;
            }
            if (typeof error?.msg !== "string") {
                return "";
            }
            const location = Array.isArray(error.loc)
                ? error.loc.filter((part) => part !== "body").join(".")
                : "";
            return location ? `${location}: ${error.msg}` : error.msg;
        })
        .filter(Boolean)
        .join("; ");
}

async function requestApi(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, options);
    if (!response.ok) {
        const responseBody = await response.text();
        let body;
        try {
            body = JSON.parse(responseBody);
        } catch {
            body = null;
        }

        const error = new Error(
            formatDetail(body?.detail) || `La requête a échoué (${response.status}).`,
        );
        error.status = response.status;
        throw error;
    }
    return response.json();
}

async function authenticate(username, password) {
    const token = await requestApi("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: new URLSearchParams({ username, password }),
    });
    sessionStorage.setItem("access_token", token.access_token);
    window.location.assign("/ticket");
}

function showLoginForm() {
    loginForm.hidden = false;
    registerForm.hidden = true;
    loginTab.setAttribute("aria-selected", "true");
    registerTab.setAttribute("aria-selected", "false");
    loginTab.className = "button button-primary";
    registerTab.className = "button button-secondary";
    authMessage.textContent = "";
    delete authMessage.dataset.state;
}

function showRegisterForm() {
    loginForm.hidden = true;
    registerForm.hidden = false;
    loginTab.setAttribute("aria-selected", "false");
    registerTab.setAttribute("aria-selected", "true");
    loginTab.className = "button button-secondary";
    registerTab.className = "button button-primary";
    authMessage.textContent = "";
    delete authMessage.dataset.state;
}

loginTab.addEventListener("click", showLoginForm);
registerTab.addEventListener("click", showRegisterForm);

loginForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitButton = loginForm.querySelector('button[type="submit"]');
    const formData = new FormData(loginForm);
    submitButton.disabled = true;
    setAuthMessage("Connexion en cours…");

    try {
        await authenticate(formData.get("username").trim(), formData.get("password"));
    } catch (error) {
        setAuthMessage(error.message, true);
    } finally {
        submitButton.disabled = false;
    }
});

registerForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    const submitButton = registerForm.querySelector('button[type="submit"]');
    const formData = new FormData(registerForm);
    const username = formData.get("username").trim();
    const password = formData.get("password");
    submitButton.disabled = true;
    setAuthMessage("Création du compte…");

    try {
        await requestApi("/api/auth/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                username,
                email: formData.get("email").trim(),
                password,
            }),
        });
        await authenticate(username, password);
    } catch (error) {
        setAuthMessage(error.message, true);
    } finally {
        submitButton.disabled = false;
    }
});

async function redirectIfAuthenticated() {
    const token = sessionStorage.getItem("access_token");
    if (!token) {
        return;
    }

    try {
        await requestApi("/api/auth/me", {
            headers: { Authorization: `Bearer ${token}` },
        });
        window.location.replace("/ticket");
    } catch (error) {
        sessionStorage.removeItem("access_token");
        if (error.status !== 401) {
            setAuthMessage(error.message, true);
        }
    }
}

redirectIfAuthenticated();
