# Development config

- **development.env** — Non-secret vars (URLs, hosts, ports, DB names). Loaded by bootstrap after `.env.secrets`, before `.env` (see CONFIG_ACQUISITION_SPEC).
- **Passwords** stay in repo-root `.env.secrets` (e.g. `ARANGO_PASS` or `ARANGO_ROOT_PASSWORD`).

**Arango 401 (not authorized):** Pre-boot connects with the username/password from canonical config. If Arango was started with a root password (e.g. Docker default `test_password`), set in `.env.secrets`:

- `ARANGO_PASS=test_password` **or** `ARANGO_ROOT_PASSWORD=test_password`

Run `python3 scripts/diagnose_arango_config.py` from repo root to see which ARANGO_* vars are set and what the platform resolves for URL, user, database, and whether the password is blank or set.

**Why 401 / “empty” password:** See [ARANGO_PASSWORD_AND_AUTH.md](../docs/ARANGO_PASSWORD_AND_AUTH.md) — you don’t create a password in Arango; it’s set when the container starts. Our compose defaults to `test_password`; put that in `.env.secrets` so the runtime matches.
