---
name: security-review
description: Use this skill when adding auth, handling user input, working with secrets, creating API endpoints, or implementing payment/sensitive features. Language/toolchain agnostic security checklist and patterns.
---

# Security Review Skill

This skill provides a language/framework/toolchain-agnostic security review checklist and remediation patterns.

**Do NOT assume Node/TypeScript/React/Supabase/etc.** Use equivalents that match the repository.

## When to Activate

- Implementing authentication or authorization
- Handling user input or file uploads
- Creating/modifying public interfaces (API endpoints, CLI commands, webhooks)
- Working with secrets or credentials
- Implementing payment features
- Storing or transmitting sensitive data
- Integrating third-party APIs
- Changing persistence/crypto/session handling

## Output Expectation

- Identify findings by severity: **CRITICAL / HIGH / MEDIUM / LOW**
- Point to **file:line** (or the smallest relevant code region)
- Provide minimal remediation steps and the **test(s) to add** when feasible

## Security Checklist

### 1) Secrets management

- Never hardcode secrets (API keys, passwords, tokens)
- Read secrets from environment variables / secret managers
- Fail fast if required secrets are missing
- Never log secrets; redact sensitive fields
- Commit only templates like `.env.example` (never real `.env*` secrets)

### 2) Input validation (all external input)

- Validate all untrusted input: HTTP, CLI args, webhooks, background jobs
- Prefer allowlist schemas/DTOs; reject unknown fields where appropriate
- Validate boundaries: 0/min/max/±1, empty/NULL, formats, lengths
- Ensure error messages do not leak sensitive details

### 3) File uploads

- Enforce size/type/extension allowlists
- Generate safe server-side filenames; never trust user-provided paths
- Store private by default; serve via controlled downloads or signed URLs
- Consider malware scanning for high-risk domains

### 4) Injection defenses

- SQL/NoSQL: parameterized queries / query builders (no string concatenation)
- Command injection: avoid shell execution; allowlist if unavoidable
- Path traversal: normalize paths; restrict to a base directory
- Template injection: never render untrusted templates/expressions

### 5) Authentication

- Passwords hashed with bcrypt/argon2 (never plaintext comparison)
- Secure sessions/cookies when applicable: HttpOnly, Secure, SameSite
- Token auth: short-lived access tokens; refresh rotation; revoke on compromise
- Rate limit login/password reset/OTP endpoints

### 6) Authorization

- Enforce object-level authorization (IDOR prevention) on read/update/delete
- Default-deny for sensitive actions; least privilege everywhere
- Validate multi-tenant boundaries if applicable

### 7) XSS / output encoding (web apps)

- Escape output by default
- If rendering user HTML, sanitize with an allowlist sanitizer
- Consider CSP headers for defense in depth

### 8) CSRF (cookie-based auth)

- Protect state-changing requests with CSRF tokens or equivalent
- Use SameSite cookies as defense in depth (not a replacement)

### 9) SSRF (server-side fetch)

- Allowlist hosts; validate scheme (`https`); block private networks
- Set timeouts and size limits; control redirects

### 10) Sensitive data exposure

- Do not expose stack traces/internal errors to users
- Redact logs; avoid storing PII unless required; encrypt at rest if needed
- Ensure TLS/HTTPS for data in transit

### 11) Dependency security

- Use the audit tool that matches the repo ecosystem (only if available/approved):
  - Node: `npm audit` / `pnpm audit` / `yarn audit`
  - Python: `pip-audit`
  - Rust: `cargo audit`
  - Multi-ecosystem: `osv-scanner`
  - PHP: `composer audit`
- Keep lockfiles committed; review new deps and licenses

## Security testing ideas (add tests when feasible)

- Auth required (401/redirect)
- Role/ownership checks (403)
- Validation failures (400)
- Rate limiting (429)
- Webhook signature verification
- SSRF allowlist rejects internal URLs
- XSS sanitization/escaping holds

## Resources

- OWASP Top 10: https://owasp.org/www-project-top-ten/
- PortSwigger Web Security Academy: https://portswigger.net/web-security
- CWE Top 25: https://cwe.mitre.org/top25/archive/2024/2024_top25_list.html

---

**Remember**: Security is not optional. When in doubt, err on the side of caution.
