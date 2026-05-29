# Legacy (original) source — preserved for reference

This directory holds the **original** Book Shop Management System exactly as it
was before the rebuild, so nothing is lost and the history of the project is
clear.

```
Book Shop Management/
├── Readme.txt                     # original install notes
├── Documentation/                 # original project report (.docx)
└── Source Code/
    ├── Python files/              # Main.py, Book.py, Tables_in_mysql.py
    └── EXE files/                 # frozen Windows executables
```

The original was a MySQL-backed **command-line** program (~230 lines). The
modern application in [`../src/bookshop`](../src/bookshop) reproduces all of its
features while fixing the issues below.

## Why it was rebuilt

| Area | Legacy behavior | Modern replacement |
|------|-----------------|--------------------|
| SQL | String-formatted queries (**SQL injection**) | Parameterized ORM queries |
| Passwords | Stored in **plain text** | bcrypt-hashed |
| Credentials | Hard-coded `root` / `manager` in source | Environment configuration |
| Prices | Read via `eval(input())` | Validated integer-cents input |
| `update_stock` | Updated **every** row (no `WHERE`) | Scoped to a single book id |
| `sell_book` | Re-read a cursor 3× (buggy) | Atomic transaction, line-items |
| Analytics | Counted cumulative totals | Correct per-period aggregation |
| Platform | Windows-only (`cls`, `startfile`) | Cross-platform Qt desktop app |

> Note: the original folder may also remain at the repository root if its files
> were locked by a running process during the rebuild; that copy is git-ignored.
