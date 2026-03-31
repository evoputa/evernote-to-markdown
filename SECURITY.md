# Security Policy

## Supported Versions

| Version | Supported |
|---|---|
| Latest (main branch) | Yes |

## Reporting a Vulnerability

If you discover a security vulnerability in this toolkit, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please email: **sme@beginefusion.com**

Include:
- A description of the vulnerability
- Steps to reproduce
- Any potential impact
- Suggested fix (if you have one)

## Response Timeline

- **Acknowledgment:** Within 48 hours
- **Assessment:** Within 5 business days
- **Fix/Patch:** As soon as reasonably possible, depending on severity

## Scope

This toolkit runs locally on your machine and processes your own Evernote data. Key areas of concern:

- **Token handling:** The export script accepts your Evernote auth token. Tokens are never stored in code, logged, or transmitted anywhere other than Evernote's API.
- **File system access:** The converter reads `.enex` files and writes `.md` files to your specified output directory. It does not access files outside the input/output paths.
- **No network calls:** After the initial Evernote download, all conversion and organization steps are fully offline.

## Best Practices for Users

- **Never commit your `evernote_backup.db`** — it contains all your notes. The `.gitignore` excludes it by default.
- **Never commit `.enex` files** — they contain your personal data.
- **Revoke your Evernote token** after migration is complete (Settings > Security > Revoke access).
- **Review the `.gitignore`** before pushing any fork to ensure no personal data is included.

## Credits

Maintained by [Evangel Oputa](https://github.com/evoputa) at [Begine Fusion](https://beginefusion.com) & [OnStack AI Labs](https://github.com/OnStack-AI-Labs).
