# Local Security Scan Report

- Date: 2026-07-16 (Asia/Saigon)
- Workspace: `team-005-ai-real-estate`
- Branch: `dev`
- Working tree: dirty (local changes included in review)
- Scope: `src/`, `FE/src/`, `scripts/`, deployment/configuration files
- Result: 2 High, 3 Medium, 1 Low

## Remediation status

Security fixes were implemented and verified after this scan:

- SEC-001: mitigated with bounded sliding-window limits by session and client IP, UUID validation, TTL eviction and regression coverage for session rotation. A shared gateway/Redis limiter remains recommended for multi-worker production deployments.
- SEC-002: resolved by requiring `customer.edit` permission and applying a per-user LLM scoring limit.
- SEC-003: mitigated with independent IP and account login throttles and `Retry-After` responses.
- SEC-004: mitigated by reducing the default JWT lifetime from eight hours to one hour, moving browser storage from persistent `localStorage` to tab-scoped `sessionStorage`, clearing legacy tokens and adding baseline browser security headers. HttpOnly cookie sessions remain the stronger long-term design.
- SEC-005: mitigated with recursive credential, email and phone redaction both when logs are written and immediately before upload.
- SEC-006: resolved by replacing `shell=True` with a fixed Git executable plus argument lists.

Verification: 235 tests passed, 1 live-LLM test skipped; changed-scope Ruff and compile checks passed; Next.js production build passed.

## Important scan note

The configured SecuSense cloud MCP exposes GitHub scans, not local-filesystem scans. The workspace has uncommitted changes, so a cloud scan would not represent the current code. Semgrep local installation was attempted with pip and uvx, but the package CDN repeatedly reset/timed out while downloading the scanner. This report therefore uses a local rule-driven source audit and manual triage. It is useful and actionable, but it is not a complete Semgrep/SecuSense engine result.

## Fix first

### SEC-001 — High — Chat rate limit is bypassable and its state can grow without bounds

Evidence:

- `src/api/agent_routes.py:69` stores timestamps in a process-global dictionary.
- `src/api/agent_routes.py:97-107` keys the limit only by `session_id` and never evicts inactive keys.
- `src/api/agent_routes.py:235` accepts the request-provided `session_id` or creates a UUID.
- `src/api/agent_routes.py:335` invokes the AI agent after the bypassable check.

Impact:

An unauthenticated client can send a new random `session_id` for every request, bypassing the five-per-minute limit. This can create conversations/messages, consume LLM quota and grow `_MESSAGE_TIMESTAMPS` until the process restarts. Multiple workers also enforce separate limits, making the control inconsistent.

Recommended fix:

1. Enforce a shared TTL rate limit in Redis or at the API gateway using client IP plus a signed server-issued session identifier.
2. Reject malformed/unissued session identifiers instead of trusting arbitrary values.
3. Add global and per-IP LLM budgets, concurrent-request limits, and a bounded fallback for development.
4. Add tests that rotate `session_id` values and verify the client is still throttled.

### SEC-002 — High — Public customer-score endpoint allows unlimited LLM calls

Evidence:

- `src/api/agent_routes.py:436-465` exposes `/agent/customer-score` without authentication or rate limiting.
- `src/services/lead_scorer.py:93-100` creates an LLM client and invokes it for each request.

Impact:

Any internet client can repeatedly invoke a paid/limited LLM through this endpoint. This enables quota exhaustion, cost abuse and service degradation independently of the chat limiter.

Recommended fix:

1. Make this an internal/admin endpoint protected by `get_current_user` plus a specific permission.
2. If public access is intentional, apply the same shared rate limiter, strict body-size limits and per-tenant budget controls.
3. Prefer the existing rule-based scorer for unauthenticated requests; reserve LLM scoring for captured leads or staff workflows.

## Other findings

### SEC-003 — Medium — Login endpoint has no brute-force protection

Evidence: `src/api/auth.py:20-25` validates credentials directly with no account/IP throttling, progressive delay or lockout.

Risk: password spraying and credential stuffing against admin/sales accounts.

Fix: add shared IP+account throttling, generic responses, security event logging and optional temporary lockout/MFA for administrators.

### SEC-004 — Medium — Long-lived admin JWT is stored in localStorage

Evidence:

- `FE/src/lib/auth.ts:22-25` reads the admin token from `localStorage`.
- `FE/src/app/admin/login/page.tsx:29` writes the access token to `localStorage`.
- `src/config.py:58` defaults token lifetime to 480 minutes.

Risk: any successful XSS or malicious same-origin script can steal an eight-hour bearer token. There is no refresh-token rotation or explicit revocation identifier in `src/services/security.py:19-34`.

Fix: prefer short-lived access tokens in Secure, HttpOnly, SameSite cookies, add refresh rotation/revocation, reduce access-token lifetime, and deploy a restrictive CSP.

### SEC-005 — Medium — AI hook logs can persist and upload sensitive prompt/tool content

Evidence:

- `scripts/log_hook.py:85-149` records prompts, tool input, tool response and transcript paths.
- `scripts/log_hook.py:176-181` persists entries locally.
- `scripts/submit_log.py:110-123` uploads complete entries to `AI_LOG_SERVER`.
- `.gitignore:65-66` prevents Git commits but does not redact or limit local/archive retention.

Risk: secrets, customer PII, source fragments or command arguments entered during AI sessions can be retained locally and transmitted to the grading endpoint.

Fix: redact credential/PII patterns before persistence, allowlist fields, truncate structured tool arguments, document consent/retention, encrypt archives, and provide a disable switch for sensitive work.

### SEC-006 — Low — Shell execution is unnecessarily enabled in hook logging

Evidence: `scripts/log_hook.py:16-18` calls `subprocess.check_output(..., shell=True)`.

Current exploitability is low because all current callers pass fixed Git commands. The helper is easy to misuse later, however.

Fix: accept an argument list and use `shell=False`, matching `scripts/log_manual.py` and `scripts/log_antigravity.py`.

## Reviewed controls and non-findings

- No high-confidence committed token/private-key patterns were found in Git-tracked files.
- Password hashing uses `PasswordHash.recommended()` (`src/services/security.py:8-16`).
- JWT verification pins the configured algorithm (`src/services/security.py:32-34`).
- Production configuration rejects known weak JWT/admin defaults and unsafe database/CORS settings (`src/config.py:127-170`).
- Customer access is scoped by permission or assigned salesperson (`src/api/customers.py:217-220, 225-251`).
- SQL found in retrieval uses static statements with bound parameters; no confirmed SQL injection was identified.
- The chat renderer does not use `dangerouslySetInnerHTML`; link scheme allowlisting is still recommended as defense in depth (`FE/src/components/chat-markdown.tsx:29-42`).

## Recommended remediation order

1. SEC-002: lock down `/agent/customer-score` immediately.
2. SEC-001: replace the session-only in-memory chat limiter.
3. SEC-003: protect `/auth/login` from credential attacks.
4. SEC-004: shorten and harden admin token handling.
5. SEC-005 and SEC-006: redact AI logs and remove `shell=True`.
