const form = document.querySelector("#ticket-form");
const tokenInput = document.querySelector("#access-token");
const formMessage = document.querySelector("#form-message");
const ticketList = document.querySelector("#ticket-list");
const ticketListMessage = document.querySelector("#ticket-list-message");

function getToken() {
    const token = tokenInput.value.trim();
    if (!token) {
        throw new Error("Saisissez d'abord votre jeton d'accès.");
    }
    return token;
}

function setFormMessage(message, isError = false) {
    formMessage.textContent = message;
    formMessage.dataset.state = isError ? "error" : "success";
}

async function requestTickets(path, options = {}) {
    const response = await fetch(path, {
        ...options,
        headers: {
            Authorization: `Bearer ${getToken()}`,
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
        time: Number(formData.get("time")),
        adopt: Number(formData.get("adopt")),
    };

    try {
        const createdTicket = await requestTickets("/api/tickets", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(ticket),
        });
        form.reset();
        document.querySelector("#time").value = "0";
        document.querySelector("#adopt").value = "1";
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
            const details = document.createElement("p");
            details.textContent = `${ticket.time} min · ${ticket.adopt} personne(s)`;

            item.append(title, description, details);
            ticketList.append(item);
        }
    } catch (error) {
        ticketListMessage.textContent = error.message;
    }
}

document.querySelector("#load-tickets").addEventListener("click", loadTickets);
