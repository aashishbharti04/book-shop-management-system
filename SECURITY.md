# Security Policy

We take the security of Book Shop Management seriously. Thank you for helping
keep the project and its users safe.

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | ✅        |

## Reporting a Vulnerability

**Please do not open a public issue for security vulnerabilities.**

Instead, report them privately:

1. Preferred: use GitHub's **[Report a vulnerability](https://github.com/aashishbharti04/book-shop-management-system/security/advisories/new)** (Security → Advisories).
2. Or email **[aashish@marketdoctorsonline.com](mailto:aashish@marketdoctorsonline.com)** with:
   - a description of the issue and its impact,
   - steps to reproduce,
   - affected version/commit.

You can expect an acknowledgement within **5 business days** and a remediation
plan once the report is validated. Please give us reasonable time to release a
fix before any public disclosure.

## Security Practices in This Project

- **Passwords** are hashed with bcrypt; plaintext passwords are never stored.
- **Database credentials** are read from the environment (`.env` / `DATABASE_URL`)
  and are never committed (`.env` and `*.db` are git-ignored).
- **All database access** uses parameterized SQLAlchemy queries — there is no
  string-formatted SQL.
- **User-supplied content** rendered into receipt HTML is escaped to prevent
  injection.
- No `eval`/`exec` is used for parsing user input (prices are parsed safely as
  integer cents).
