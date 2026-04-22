# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| latest  | :white_check_mark: |
| < latest| :x:                |

We maintain security updates for the latest release only.

## Reporting a Vulnerability

**Do not report security vulnerabilities through public GitHub issues.**

Report vulnerabilities privately via:
- [GitHub Security Advisories](https://github.com/NimbleOx/fivetwenty/security/advisories/new)
- Include: description, reproduction steps, impact, and suggested fix (if any)

**Response timeline:**
- Acknowledgment within 48 hours
- Critical fixes within 7 days
- Public credit for responsible disclosure (unless you prefer anonymity)

## Security Best Practices

### Credentials
- Never commit API tokens to version control
- Use environment variables (`.env` files in `.gitignore`)
- Rotate credentials regularly
- Use practice accounts for development

### Code Safety
- Use `Decimal` for financial calculations (never `float`)
- Sanitize logs to exclude API tokens
- Implement rate limiting to prevent API key suspension
- Handle streaming reconnections to avoid duplicate trades

### Trading
- Start with paper trading (practice environment)
- Implement position limits and risk management
- Never automate without thorough testing

## Scope

**Covered:**
- FiveTwenty library code
- Documentation examples

**Not covered:**
- OANDA's API infrastructure
- Third-party dependencies
- User applications
- Trading strategies or financial outcomes

---

**Disclaimer**: Trading involves substantial risk. This library is provided "as is" without warranty. Test thoroughly and trade responsibly.
