# Authentication and authorisation (B-02)

Registration, login and the trusted authentication boundary. Covers **FR-001** and **NFR-005**
(server-side authorisation). Code: `backend/src/skillmatch/modules/identity` (accounts, hashing, use cases),
`backend/src/skillmatch/core/security.py` (token signing and verification) and
`backend/src/skillmatch/api/{auth,deps}.py` (endpoints and dependencies).

## Endpoints

| Endpoint | Access | Purpose |
|---|---|---|
| `POST /api/v1/auth/register` | public | Create a `talento` (candidate) or `empresa` (company) account |
| `POST /api/v1/auth/login` | public | Exchange email and password for a bearer token, the identity and the role |
| `GET /api/v1/auth/me` | any signed-in account | The account behind the token, read from the database |

The role names of the data model are the public vocabulary: **Candidate = `talento`, Company = `empresa`,
Admin = `admin`**. Every error is an RFC 9457 `application/problem+json` document. The contract is
`backend/openapi.json`, kept in sync by `tests/api/test_openapi_contract.py`.

## How a request is authenticated

1. `POST /auth/login` checks the password against the stored hash and signs a token (HS256) with
   `SKILLMATCH_AUTH_SERVICE_SECRET`. The token carries the account id, an expiry and a role claim for information only.
2. Protected routes verify the signature and expiry (`core/security.py`), then **reload the account from the
   database** (`api/deps.py::get_current_user`). The account must exist and be `active`.
3. Authorisation (`require_roles`, `verify_resource_ownership`) uses the **role stored in the database**. A forged role
   claim, even with a valid signature, cannot elevate anyone.

Nothing the client sends freely (headers, ids, roles in a body) is ever used as identity or permission.

## Decisions

| Topic | Decision | Why |
|---|---|---|
| Password hashing | scrypt from the standard library, N=2^17, r=8, p=1, 16-byte random salt, PHC string, NFKC-normalised input, constant-time comparison | OWASP-listed algorithm at OWASP's minimum cost, and **no new dependency** (`AGENTS.md` asks to review any new library). Argon2id is the preferred algorithm; swapping it in only touches `passwords.py` |
| Hash upgrade | A hash made with other parameters is re-hashed after a successful login | Costs can be raised without a migration |
| Blocking work | Hashing runs in a worker thread (`asyncio.to_thread`) | Keeps the event loop responsive |
| Password policy | 12 to 128 characters, no composition rules, not only whitespace | NIST SP 800-63B; the upper bound limits the work one request can force |
| Registration | Public roles are only `talento` and `empresa`; `admin` fails validation. Unknown fields (`status`, `is_admin`…) are rejected | Privilege escalation through the public API is impossible by construction |
| Login failures | One message and status for unknown email, wrong password, no password and inactive account; a hash is always verified (a dummy one when there is no account) | Limits account enumeration, also by timing |
| Token lifetime | `SKILLMATCH_AUTH_TOKEN_TTL_SECONDS` (default 900), returned as `expires_in` | Short-lived tokens, configurable |
| Fail closed | No signing secret: login answers `503 authentication_unavailable`; staging and production refuse to start without a 32+ character secret | Never sign with an empty or default key |
| Cache | Login responses carry `Cache-Control: no-store` | RFC 6749, section 5.1 |
| Logs | Passwords, hashes, tokens and the secret are never logged (a test checks it); validation errors never echo submitted values | NFR-005 |

## Configuration

| Variable | Default | Notes |
|---|---|---|
| `SKILLMATCH_AUTH_SERVICE_SECRET` | empty | At least 32 characters, **required** in `staging` and `production`. Generate: `python -c "import secrets; print(secrets.token_urlsafe(48))"` |
| `SKILLMATCH_AUTH_TOKEN_TTL_SECONDS` | `900` | Access token lifetime in seconds |

Never commit the secret. Rotating it invalidates every outstanding token.

## Acceptance criteria and where they are tested

| Criterion | Tests |
|---|---|
| Registration and login work against the database | `tests/api/test_auth_endpoints.py` (in-memory database through the real API) |
| Passwords stored with a secure hash | `test_the_password_is_stored_only_as_a_scrypt_hash`, `tests/unit/test_passwords.py` |
| Login returns a valid token, the real identity and role | `test_login_returns_a_bearer_token_with_the_real_identity_and_role`, `test_the_token_is_signed_for_the_account…` |
| Public registration cannot create admins | `test_the_public_registration_cannot_create_other_roles`, `tests/unit/test_auth_schemas.py` |
| Bad credentials, unknown and inactive users | login failure tests |
| Token issue, expiry and verification | token tests here and `tests/unit/test_security.py` |
| No token or invalid token | `test_protected_routes_need_a_credential`, garbage and expired token tests |
| Unauthorised role, cross-account access, ownership | role tests here and `tests/api/test_cross_account_access.py` |
| Identity and role come from the database | `test_the_role_comes_from_the_database_not_from_the_token`, forged-claim test |
| No secrets in logs | `test_registration_and_login_never_write_secrets_to_the_logs` |
| Endpoints documented in OpenAPI | `tests/api/test_openapi_contract.py` |

## Known limitations

| Limitation | Note |
|---|---|
| No rate limiting or lockout on `/auth/login` and `/auth/register` | Task B-09. scrypt at this cost is also a memory-based denial-of-service vector until it exists |
| Registration answers `409` for a taken email | Reveals that the address exists; accepted trade-off, mitigated by rate limiting |
| No refresh tokens, logout or revocation | Tokens simply expire; suspending an account takes effect on the next request |
| No email verification, password reset or MFA | Out of scope for B-02 |
| Creating the first administrator | Not possible through the API by design; use a trusted script or the seed loader (S-05) |
| Passwords are not checked against breached-password lists | Possible later improvement |
