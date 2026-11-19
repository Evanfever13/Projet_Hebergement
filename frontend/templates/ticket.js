const form = document.querySelector("#ticket-form");
const formMessage = document.querySelector("#form-message");
const ticketList = document.querySelector("#ticket-list");
const ticketListMessage = document.querySelector("#ticket-list-message");
const API_BASE_URL = "https://projet-hebergement.onrender.com";
const accountName = document.querySelector("#account-name");
const logoutButton = document.querySelector("#logout");
let currentUser = null;

function setFormMessage(message, isError = false) {
    formMessage.textContent = message;
    formMessage.dataset.state = isError ? "error" : "success";
}

async function requestTickets(path, options = {}) {
    const token = sessionStorage.getItem("access_token");
    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...options,
        headers: {
            ...(options.headers || {}),
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
    });

    if (!response.ok) {
        const responseBody = await response.text();
        let detail;
        try {
            detail = JSON.parse(responseBody).detail;
        } catch {
            detail = null;
        }

        const message = Array.isArray(detail)
            ? detail
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
                .join("; ")
            : detail;
        if (response.status === 401) {
            sessionStorage.removeItem("access_token");
            window.location.replace("/login");
        }
        throw new Error(
            typeof message === "string" && message
                ? message
                : `La requête a échoué (${response.status}).`,
        );
    }
    return response.status === 204 ? null : response.json();
}

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    setFormMessage("Envoi en cours…");

    const formData = new FormData(form);
    const ticket = {
        title: formData.get("title").trim(),
        description: formData.get("description").trim(),
    };

    try {
        const createdTicket = await requestTickets("/api/tickets", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(ticket),
        });
        form.reset();
        setFormMessage(`Ticket « ${createdTicket.title} » créé.`);
        await loadTickets();
    } catch (error) {
        setFormMessage(error.message, true);
    }
});

async function loadTickets() {
    ticketListMessage.textContent = "Chargement…";
    ticketList.replaceChildren();

    try {
        const tickets = await requestTickets("/api/tickets");
        if (tickets.length === 0) {
            ticketListMessage.textContent = "Aucun ticket pour le moment.";
            return;
        }

        ticketListMessage.textContent = "";
        for (const ticket of tickets) {
            const item = document.createElement("li");
            item.className = "ticket-card";

            const title = document.createElement("h3");
            title.textContent = ticket.title;
            const description = document.createElement("p");
            description.textContent = ticket.description;

            const createdAt = document.createElement("p");
            const date = new Date(ticket.created_at);
            createdAt.textContent = Number.isNaN(date.getTime())
                ? `Créé le ${ticket.created_at}`
                : `Créé le ${date.toLocaleString("fr-FR")}`;

            const status = document.createElement("p");
            status.textContent = `Statut : ${ticket.status}`;

            const editButton = document.createElement("button");
            editButton.className = "button button-secondary";
            editButton.type = "button";
            editButton.textContent = "Modifier le statut";

            const editForm = document.createElement("form");
            editForm.className = "ticket-status-form";
            editForm.hidden = true;

            const statusLabel = document.createElement("label");
            statusLabel.htmlFor = `ticket-status-${ticket.id}`;
            statusLabel.textContent = "Nouveau statut";

            const statusSelect = document.createElement("select");
            statusSelect.id = statusLabel.htmlFor;
            statusSelect.name = "status";
            for (const value of ["Ouvert", "En cours", "Terminé"]) {
                const option = document.createElement("option");
                option.value = value;
                option.textContent = value;
                option.selected = value === ticket.status;
                statusSelect.append(option);
            }

            const saveButton = document.createElement("button");
            saveButton.className = "button button-primary";
            saveButton.type = "submit";
            saveButton.textContent = "Enregistrer";

            const cancelButton = document.createElement("button");
            cancelButton.className = "button button-secondary";
            cancelButton.type = "button";
            cancelButton.textContent = "Annuler";

            const editMessage = document.createElement("p");
            editMessage.className = "ticket-edit-message";
            editMessage.setAttribute("role", "status");

            editForm.append(statusLabel, statusSelect, saveButton, cancelButton, editMessage);
            item.append(title, description, createdAt, status, editButton, editForm);

            const cardMessage = document.createElement("p");
            cardMessage.className = "ticket-edit-message";
            cardMessage.setAttribute("role", "status");
            item.append(cardMessage);

            if (currentUser?.role === "admin") {
                const deleteButton = document.createElement("button");
                deleteButton.className = "button button-danger";
                deleteButton.type = "button";
                deleteButton.textContent = "Supprimer le ticket";
                item.append(deleteButton);
                deleteButton.addEventListener("click", async () => {
                    if (!window.confirm(`Supprimer le ticket « ${ticket.title} » ?`)) {
                        return;
                    }

                    deleteButton.disabled = true;
                    try {
                        await requestTickets(`/api/tickets/${ticket.id}`, {
                            method: "DELETE",
                        });
                        await loadTickets();
                    } catch (error) {
                        cardMessage.textContent = error.message;
                        cardMessage.dataset.state = "error";
                        deleteButton.disabled = false;
                    }
                });
            }

            editButton.addEventListener("click", () => {
                statusSelect.value = ticket.status;
                editButton.hidden = true;
                editForm.hidden = false;
                statusSelect.focus();
            });

            cancelButton.addEventListener("click", () => {
                editForm.hidden = true;
                editButton.hidden = false;
                editMessage.textContent = "";
                delete editMessage.dataset.state;
            });

            editForm.addEventListener("submit", async (event) => {
                event.preventDefault();
                saveButton.disabled = true;
                editMessage.textContent = "";
                delete editMessage.dataset.state;

                try {
                    const updatedTicket = await requestTickets(`/api/tickets/${ticket.id}`, {
                        method: "PATCH",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ status: statusSelect.value }),
                    });
                    ticket.status = updatedTicket.status;
                    status.textContent = `Statut : ${updatedTicket.status}`;
                    editForm.hidden = true;
                    editButton.hidden = false;
                } catch (error) {
                    editMessage.textContent = error.message;
                    editMessage.dataset.state = "error";
                } finally {
                    saveButton.disabled = false;
                }
            });

            ticketList.append(item);
        }
    } catch (error) {
        ticketListMessage.textContent = error.message;
    }
}

document.querySelector("#load-tickets").addEventListener("click", loadTickets);

logoutButton.addEventListener("click", () => {
    sessionStorage.removeItem("access_token");
    window.location.replace("/login");
});

async function initializeTicketsPage() {
    if (!sessionStorage.getItem("access_token")) {
        window.location.replace("/login");
        return;
    }

    try {
        currentUser = await requestTickets("/api/auth/me");
        accountName.textContent = currentUser.username;
        await loadTickets();
    } catch (error) {
        ticketListMessage.textContent = error.message;
    }
}

initializeTicketsPage();
