"""Populate the database with demo data for first-run / development."""

from __future__ import annotations

from ..core.exceptions import UsernameTakenError
from ..data.engine import Database
from .container import Container
from .dto import CartLine

DEMO_USERNAME = "demo"
DEMO_PASSWORD = "demo1234"

# (title, author, publisher, isbn, price_cents, stock_qty)
DEMO_BOOKS: list[tuple[str, str, str, str, int, int]] = [
    ("The Pragmatic Programmer", "Hunt & Thomas", "Addison-Wesley", "9780201616224", 4299, 12),
    ("Clean Code", "Robert C. Martin", "Prentice Hall", "9780132350884", 3899, 8),
    ("Design Patterns", "Gang of Four", "Addison-Wesley", "9780201633610", 5499, 5),
    ("Introduction to Algorithms", "Cormen et al.", "MIT Press", "9780262046305", 8999, 3),
    ("Fluent Python", "Luciano Ramalho", "O'Reilly", "9781492056355", 6199, 7),
    ("The Mythical Man-Month", "Fred Brooks", "Addison-Wesley", "9780201835953", 2999, 2),
    ("Refactoring", "Martin Fowler", "Addison-Wesley", "9780134757599", 5999, 6),
    ("You Don't Know JS", "Kyle Simpson", "O'Reilly", "9781491924464", 2499, 0),  # out of stock
]


def seed_demo_data(*, reset: bool = False, database: Database | None = None) -> str:
    db = database or Database()
    if reset:
        db.drop_all()
    db.create_all()

    container = Container(db)
    services = container.services

    # Get-or-create the demo user.
    user = services.auth.login(DEMO_USERNAME, DEMO_PASSWORD)
    user_created = False
    if user is None:
        try:
            user = services.auth.register(DEMO_USERNAME, DEMO_PASSWORD, DEMO_PASSWORD)
            user_created = True
        except UsernameTakenError:
            user = services.auth.login(DEMO_USERNAME, DEMO_PASSWORD)

    # Seed books only if the catalogue is empty.
    book_ids: list[int] = []
    books_created = 0
    if services.inventory.count_books() == 0:
        for title, author, publisher, isbn, price_cents, qty in DEMO_BOOKS:
            dto = services.inventory.add_book(
                title=title,
                author=author,
                publisher=publisher,
                isbn=isbn,
                price_cents=price_cents,
                initial_qty=qty,
            )
            book_ids.append(dto.id)
            books_created += 1

    # Seed a couple of sales so the dashboard/analytics have data.
    sales_created = 0
    if book_ids and len(book_ids) >= 3:
        user_id = user.id if user else None
        services.sales.create_sale(
            [CartLine(book_ids[0], 2), CartLine(book_ids[1], 1)],
            customer_name="Ada Lovelace",
            customer_phone="555-0100",
            user_id=user_id,
        )
        services.sales.create_sale(
            [CartLine(book_ids[2], 1), CartLine(book_ids[4], 3)],
            customer_name="Alan Turing",
            user_id=user_id,
        )
        sales_created = 2

    return (
        f"Seed complete - user {'created' if user_created else 'present'} "
        f"({DEMO_USERNAME}/{DEMO_PASSWORD}), "
        f"{books_created} books added, {sales_created} sales recorded."
    )
