from fastapi import APIRouter, Response, status

from backend.src.schemas.tickets import TicketResponse
from backend.src.services.tickets import (
    create_ticket,
    delete_ticket,
    get_ticket,
    list_tickets,
    update_ticket,
)

router = APIRouter(prefix="/api/tickets", tags=["Tickets"])

router.add_api_route(
    path="",
    endpoint=list_tickets,
    methods=["GET"],
    response_model=list[TicketResponse],
    status_code=status.HTTP_200_OK,
    summary="Lister les tickets",
)

router.add_api_route(
    path="",
    endpoint=create_ticket,
    methods=["POST"],
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un ticket",
)

router.add_api_route(
    path="/{ticket_id}",
    endpoint=get_ticket,
    methods=["GET"],
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Consulter un ticket accessible",
)

router.add_api_route(
    path="/{ticket_id}",
    endpoint=update_ticket,
    methods=["PATCH"],
    response_model=TicketResponse,
    status_code=status.HTTP_200_OK,
    summary="Mettre à jour un ticket",
)

router.add_api_route(
    path="/{ticket_id}",
    endpoint=delete_ticket,
    methods=["DELETE"],
    response_class=Response,
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un ticket",
)
