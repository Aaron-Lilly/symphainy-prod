# Arango password and auth: what’s going on

## You don’t “create” a password in Arango

The root password is **set when Arango starts** (in Docker, via the `ARANGO_ROOT_PASSWORD` env var). There’s no separate step where you “create” a password inside Arango.

So:

- **Server side:** Whatever password (if any) Arango was started with is the one it expects.
- **Client side:** The runtime must send that same password (in `.env.secrets` as `ARANGO_PASS` or `ARANGO_ROOT_PASSWORD`).

If they don’t match → 401 (not authorized).

---

## How it works in your stack

In `docker-compose.yml` the Arango service has:

```yaml
environment:
  ARANGO_ROOT_PASSWORD: ${ARANGO_ROOT_PASSWORD:-test_password}
```

So:

- If you **don’t** set `ARANGO_ROOT_PASSWORD` when you run `docker-compose up`, Arango is started with password **`test_password`** (the default after `:-`).
- The stack never had “no password” on the server: it has always had a password (default `test_password`) unless you explicitly chose something else.

So “we didn’t put a password anywhere” usually means “we didn’t put it in `.env.secrets`” — but Arango itself was still started with `test_password` by compose. The runtime then sent no password → 401.

---

## Two ways to fix it

### Option A: Use the password Arango was started with (recommended)

Arango is already using a password (default `test_password`). Tell the runtime the same value.

In **`.env.secrets`** set either:

- `ARANGO_PASS=test_password`, or  
- `ARANGO_ROOT_PASSWORD=test_password`

No change to docker-compose. Restart is not required for Arango; just (re)start the runtime so it reads the updated `.env.secrets`.

---

### Option B: Run Arango with no auth (dev only)

If you really want “empty” password (no auth), you have to **start** Arango that way.

1. In **docker-compose.yml**, under the `arango` service `environment`, add:
   ```yaml
   ARANGO_NO_AUTH: "1"
   ```
   and remove or comment out the `ARANGO_ROOT_PASSWORD` line (otherwise the image may still set a password).

2. Recreate the Arango container so it starts with no auth:
   ```bash
   docker-compose stop arango
   docker-compose rm -f arango   # if you want a clean start
   docker-compose up -d arango
   ```

3. In **`.env.secrets`** keep:
   - `ARANGO_PASS=` (blank)  
   or leave it unset.

**Warning:** No auth is only for local/dev. Don’t use it if Arango is reachable from the internet.

---

## Summary

| Question | Answer |
|----------|--------|
| How do we “create” a password for Arango? | You don’t create it inside Arango. You set it when Arango **starts** (e.g. `ARANGO_ROOT_PASSWORD` in Docker). |
| Was it ever “empty” in our stack? | On the **server**: no — compose has always used a default password (`test_password`) unless you override. On the **client**: yes — we didn’t put that password in `.env.secrets`, so the runtime sent blank → 401. |
| Easiest fix? | Put `ARANGO_PASS=test_password` (or `ARANGO_ROOT_PASSWORD=test_password`) in `.env.secrets` so the runtime uses the same password Arango was started with. |
