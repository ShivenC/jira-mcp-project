# mcp_server.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="MCP Server")

class Ticket(BaseModel):
    key: str
    summary: str
    description: str
    priority: str
    labels: List[str]
    status: str  # "In Progress" or "Done"
    due_date: Optional[str] = None

ticket_store: List[Ticket] = []

@app.get("/tickets", response_model=List[Ticket])
def get_all_tickets(status: Optional[str] = None):
    if status:
        return [t for t in ticket_store if t.status == status]
    return ticket_store

@app.post("/tickets")
def add_ticket(ticket: Ticket):
    ticket_store.append(ticket)
    return {"message": f"Ticket {ticket.key} added to MCP"}

@app.get("/")
def root():
    return {"message": "MCP Server running"}

@app.delete("/tickets")
def clear_tickets():
    ticket_store.clear()
    return {"message": "All tickets cleared"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
