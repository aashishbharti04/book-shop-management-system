# Service-layer API reference

The application has no network API; its public "API" is the **service layer**
(`bookshop.services`). The UI and CLI call these methods only. Every service is
constructed with a SQLAlchemy `sessionmaker` (wired by `Container`), owns its
own transaction per call, and returns immutable **DTOs** — never ORM objects.

Get them via the container:

```python
from bookshop.services.container import Container
services = Container().services
services.auth        # AuthService
services.inventory   # InventoryService
services.sales       # SalesService
services.analytics   # AnalyticsService
services.receipts    # ReceiptService
```

## AuthService

| Method | Returns | Notes |
|--------|---------|-------|
| `register(username, password, confirm) -> UserDTO` | the new user | Validates input & password policy; raises `UsernameTakenError` / `ValidationError` / `PasswordPolicyError`. |
| `login(username, password) -> UserDTO \| None` | user or `None` | Returns `None` on any failure (no username enumeration). |

## InventoryService

| Method | Returns | Notes |
|--------|---------|-------|
| `add_book(*, title, price_cents, author=None, publisher=None, isbn=None, initial_qty=0) -> BookDTO` | new book | Rejects empty title, negative price/qty, duplicate ISBN. |
| `update_book(book_id, **fields) -> BookDTO` | updated book | Scoped to one id. Editable: `title, author, publisher, isbn, price_cents`. Raises `NotFoundError`. |
| `restock(book_id, quantity) -> BookDTO` | updated book | `quantity` must be positive. |
| `get_book(book_id) -> BookDTO` | book | Raises `NotFoundError`. |
| `list_books(*, search=None, sort_by="title", order="asc", limit=None, offset=0) -> list[BookDTO]` | books | `sort_by` is whitelisted. |
| `count_books(search=None) -> int` | count | |

## SalesService

| Method | Returns | Notes |
|--------|---------|-------|
| `create_sale(cart, *, customer_name=None, customer_phone=None, user_id=None) -> SaleDTO` | the recorded sale | `cart` is a list of `CartLine`. **Atomic**: stock is decremented with a guarded UPDATE; raises `OutOfStockError` and rolls back if any line lacks stock. Unit prices are captured at sale time. |
| `get_sale(sale_id) -> SaleDTO` | sale | Raises `NotFoundError`. |
| `recent_sales(limit=10) -> list[SaleDTO]` | recent sales | Newest first. |

## AnalyticsService

| Method | Returns | Notes |
|--------|---------|-------|
| `monthly_sales(year, month) -> list[BookSalesDTO]` | per-book units & revenue | Half-open `[start, end)` month range. |
| `sales_for_period(start, end) -> list[BookSalesDTO]` | per-book totals | |
| `revenue_for_period(start, end) -> int` | cents | |
| `top_books(limit, start, end) -> list[BookSalesDTO]` | top N | |
| `dashboard_summary(*, now=None) -> DashboardDTO` | KPI snapshot | Uses scalar count/sum queries. |

## ReceiptService

| Method | Returns | Notes |
|--------|---------|-------|
| `render_text(sale) -> str` | plain-text receipt | |
| `render_html(sale) -> str` | HTML receipt | User content is escaped. |
| `export_pdf(sale, path) -> Path` | file path | Uses `QPdfWriter`; works headless. |
| `print_receipt(sale, parent=None) -> bool` | printed? | Opens the OS print dialog. |

## DTOs (`bookshop.services.dto`)

All are frozen dataclasses (immutable, thread-safe):

- **UserDTO** — `id, username, role`
- **BookDTO** — `id, title, author, publisher, isbn, price_cents, stock_qty`; helpers `price_display`, `in_stock`, `status(threshold)`
- **CartLine** — `book_id, quantity`
- **SaleItemDTO** — `book_id, title, quantity, unit_price_cents, line_total_cents` (+ display helpers)
- **SaleDTO** — `id, total_cents, created_at, items, customer_name, customer_phone, sold_by` (+ `total_display`, `item_count`)
- **BookSalesDTO** — `book_id, title, quantity, revenue_cents` (+ `revenue_display`)
- **DashboardDTO** — KPI counters (+ display helpers)

> Money is always integer **cents**. Format for display with `bookshop.core.money.format_money`.
