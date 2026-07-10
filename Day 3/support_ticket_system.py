

from abc import ABC, abstractmethod
import functools
import json
import logging

import requests


logging.basicConfig(level=logging.INFO, format="%(levelname)-7s | %(message)s")
logger = logging.getLogger("helpdesk")


def track(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"action: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

class Ticket(ABC):
    _next_id = 100                       

    def __init__(self, title, priority):
        self._title = title              
        self._priority = priority
        self.status = "open"
        Ticket._next_id += 1
        self.ticket_id = Ticket._next_id

    @property                            
    def priority(self):
        return self._priority

    @priority.setter
    def priority(self, value):
        if value not in ("low", "medium", "high"):
            raise ValueError("priority must be low, medium, or high")
        self._priority = value

    @abstractmethod                      
    def category(self):
        ...

    @abstractmethod
    def sla_hours(self):                 
        ...

    def to_dict(self):                   
        return {
            "id": self.ticket_id,
            "title": self._title,
            "category": self.category(),
            "priority": self._priority,
            "sla_hours": self.sla_hours(),
            "status": self.status,
        }

    def __str__(self):
        return f"#{self.ticket_id} [{self.category()}/{self._priority}] {self._title} ({self.status})"


class BugTicket(Ticket):
    def category(self):
        return "Bug"

    def sla_hours(self):
        return {"high": 4, "medium": 24, "low": 72}[self._priority]


class FeatureRequest(Ticket):
    def category(self):
        return "Feature"

    def sla_hours(self):
        return 168  

class TicketQueue:
    def __init__(self):
        self._tickets = []

    def add(self, ticket):
        self._tickets.append(ticket)

    def __iter__(self):
        self._i = 0
        return self

    def __next__(self):
        if self._i >= len(self._tickets):
            raise StopIteration
        ticket = self._tickets[self._i]
        self._i += 1
        return ticket


def open_tickets(queue):
    for ticket in queue:
        if ticket.status == "open":
            yield ticket


def check_latest_version(package):
    """Real IT task: is a library outdated? Ask PyPI's JSON API."""
    try:
        url = f"https://pypi.org/pypi/{package}/json"
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        return r.json()["info"]["version"]
    except requests.exceptions.RequestException as e:
        logger.warning(f"Version check failed for '{package}': {e}")
        return None


class TicketStore:
    def __init__(self, path):
        self.path = path
        self.data = []

    def __enter__(self):
        logger.info(f"opening report file: {self.path}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=2)      
        logger.info(f"wrote {len(self.data)} ticket(s) to {self.path}")
        return False                               

    def export(self, queue):
        self.data = [t.to_dict() for t in queue]


@track
def resolve(ticket):
    ticket.status = "resolved"
    return ticket


def main():
    queue = TicketQueue()
    queue.add(BugTicket("Login button unresponsive on mobile", "high"))
    queue.add(FeatureRequest("Add dark mode to dashboard", "medium"))
    queue.add(BugTicket("Typo in invoice footer", "low"))

    print("=== All open tickets (with SLA) ===")
    for ticket in open_tickets(queue):            
        print(f"  {ticket}  ->  respond within {ticket.sla_hours()}h")


    version = check_latest_version("requests")
    print(f"\nLatest version of 'requests' on PyPI: {version or 'unavailable'}")

    print("\nResolving the two bug tickets...\n")
    for ticket in queue:
        if ticket.category() == "Bug":
            resolve(ticket)                        

    with TicketStore("tickets_report.json") as store:
        store.export(queue)

    print("\n=== Still open after resolving bugs ===")
    for ticket in open_tickets(queue):
        print(f"  {ticket}")


if __name__ == "__main__":
    main()
