const form = document.querySelector("#ticket-form");
const formMessage = document.querySelector("#form-message");
const ticketList = document.querySelector("#ticket-list");
const ticketListMessage = document.querySelector("#ticket-list-message");
const apiBaseUrl = (window.APP_CONFIG?.apiUrl || "").replace(/\/+$/, "");

function apiUrl(path) {
    return `${apiBaseUrl}${path}`;
}

function setFormMessage(message, isError = false) {
    formMessage.textContent = message;
    formMessage.dataset.state = isError ? "error" : "success";
}

async function requestTickets(path, options = {}) {
    const response = await fetch(apiUrl(path), {
        ...options,
        headers: {
            ...(options.headers || {}),
        },
    });

    if (!response.ok) {
        const body = await response.json().catch(() => ({}));
        throw new Error(body.detail || `La requête a échoué (${response.status}).`);
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
            ticketListMessage.textContent = "Vous n'avez pas encore de ticket.";
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
            const status = document.createElement("p");
            status.textContent = `Statut : ${ticket.status}`;
            const createdAt = document.createElement("p");
            createdAt.textContent = `Créé le : ${new Date(ticket.created_at).toLocaleString("fr-FR")}`;

            const statusSelect = document.createElement("select");
            statusSelect.setAttribute("aria-label", `Modifier le statut de ${ticket.title}`);
            for (const value of ["Ouvert", "En cours", "Résolu"]) {
                const option = document.createElement("option");
                option.value = value;
                option.textContent = value;
                option.selected = value === ticket.status;
                statusSelect.append(option);
            }
            statusSelect.addEventListener("change", async () => {
                try {
                    await requestTickets(`/api/tickets/${ticket.id}`, {
                        method: "PATCH",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ status: statusSelect.value }),
                    });
                    await loadTickets();
                } catch (error) {
                    ticketListMessage.textContent = error.message;
                }
            });

            const deleteButton = document.createElement("button");
            deleteButton.type = "button";
            deleteButton.className = "button button-secondary";
            deleteButton.textContent = "Supprimer";
            deleteButton.addEventListener("click", async () => {
                try {
                    await requestTickets(`/api/tickets/${ticket.id}`, {
                        method: "DELETE",
                    });
                    await loadTickets();
                } catch (error) {
                    ticketListMessage.textContent = error.message;
                }
            });

            item.append(title, description, status, createdAt, statusSelect, deleteButton);
            ticketList.append(item);
        }
    } catch (error) {
        ticketListMessage.textContent = error.message;
    }
}

document.querySelector("#load-tickets").addEventListener("click", loadTickets);
loadTickets();
