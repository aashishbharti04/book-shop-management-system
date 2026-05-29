"""Point-of-sale: create sales atomically with guarded stock decrements."""

from __future__ import annotations

from collections.abc import Sequence

from ..core.exceptions import NotFoundError, OutOfStockError, ValidationError
from ..data.models import Sale, SaleItem
from ..data.repositories import BookRepository, SaleRepository, UserRepository
from .base import BaseService, to_sale_dto
from .dto import CartLine, SaleDTO, SaleItemDTO

MAX_PHONE_LENGTH = 32


def _clean(value: str | None, max_length: int | None = None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    if max_length is not None and len(value) > max_length:
        raise ValidationError(f"Value must be at most {max_length} characters.")
    return value


class SalesService(BaseService):
    def create_sale(
        self,
        cart: Sequence[CartLine],
        *,
        customer_name: str | None = None,
        customer_phone: str | None = None,
        user_id: int | None = None,
    ) -> SaleDTO:
        """Record a sale in a single transaction.

        For each line, stock is decremented with a guarded ``UPDATE`` that can
        never drive stock negative; if any line lacks stock the **entire** sale
        rolls back. The unit price is captured from the book at sale time so a
        later price change does not rewrite history. Any client-supplied price
        is ignored — totals are computed server-side.
        """

        if not cart:
            raise ValidationError("Cannot complete a sale with an empty cart.")

        # Consolidate duplicate book lines so each book is decremented once.
        quantities: dict[int, int] = {}
        for line in cart:
            if line.quantity <= 0:
                raise ValidationError("Each line quantity must be a positive number.")
            quantities[line.book_id] = quantities.get(line.book_id, 0) + line.quantity

        customer_name = _clean(customer_name, 255)
        customer_phone = _clean(customer_phone, MAX_PHONE_LENGTH)

        with self._unit_of_work() as session:
            book_repo = BookRepository(session)
            sale_repo = SaleRepository(session)

            sale = Sale(
                customer_name=customer_name,
                customer_phone=customer_phone,
                sold_by_user_id=user_id,
                total_cents=0,
            )
            sale_repo.add(sale)  # flush -> sale.id available

            item_dtos: list[SaleItemDTO] = []
            total_cents = 0
            for book_id, quantity in quantities.items():
                book = book_repo.get(book_id)
                if book is None:
                    raise NotFoundError(f"Book {book_id} does not exist.")

                affected = book_repo.decrement_stock(book_id, quantity)
                if affected != 1:
                    # Guarded UPDATE matched no row -> insufficient stock.
                    raise OutOfStockError(book_id, quantity, book.stock_qty)

                unit_price = book.price_cents
                line_total = unit_price * quantity
                total_cents += line_total
                session.add(
                    SaleItem(
                        sale_id=sale.id,
                        book_id=book_id,
                        quantity=quantity,
                        unit_price_cents=unit_price,
                        line_total_cents=line_total,
                    )
                )
                item_dtos.append(
                    SaleItemDTO(
                        book_id=book_id,
                        title=book.title,
                        quantity=quantity,
                        unit_price_cents=unit_price,
                        line_total_cents=line_total,
                    )
                )

            sale.total_cents = total_cents
            if user_id is not None:
                # Attach the cashier so the receipt can show who made the sale.
                sale.sold_by = UserRepository(session).get(user_id)
            session.flush()
            return to_sale_dto(sale, tuple(item_dtos))

    def get_sale(self, sale_id: int) -> SaleDTO:
        with self._unit_of_work() as session:
            sale = SaleRepository(session).get(sale_id)
            if sale is None:
                raise NotFoundError(f"Sale {sale_id} does not exist.")
            items = tuple(
                SaleItemDTO(
                    book_id=item.book_id,
                    title=item.book.title if item.book is not None else "(removed)",
                    quantity=item.quantity,
                    unit_price_cents=item.unit_price_cents,
                    line_total_cents=item.line_total_cents,
                )
                for item in sale.items
            )
            return to_sale_dto(sale, items)

    def recent_sales(self, limit: int = 10) -> list[SaleDTO]:
        with self._unit_of_work() as session:
            sales = SaleRepository(session).recent(limit)
            result: list[SaleDTO] = []
            for sale in sales:
                items = tuple(
                    SaleItemDTO(
                        book_id=item.book_id,
                        title=item.book.title if item.book is not None else "(removed)",
                        quantity=item.quantity,
                        unit_price_cents=item.unit_price_cents,
                        line_total_cents=item.line_total_cents,
                    )
                    for item in sale.items
                )
                result.append(to_sale_dto(sale, items))
            return result
