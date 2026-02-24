# Security Policy

## Supported Versions

| Version | Supported |
| --- | --- |
| Latest (`main`) | ✅ |
| Older commits | ❌ |

## Reporting a Vulnerability

If you discover a security vulnerability in **IPL Viz**, please report it responsibly.

**Do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please email the maintainer directly:

📧 **[manojpisini@gmail.com](mailto:manojpisini@gmail.com)**

Include the following in your report:

- A clear description of the vulnerability
- Steps to reproduce the issue
- The potential impact
- Any suggested fix (optional, but appreciated)

## Response Timeline

| Stage | Timeframe |
| --- | --- |
| Acknowledgement | Within **48 hours** |
| Initial assessment | Within **5 business days** |
| Patch release (if confirmed) | Within **14 business days** |

You will be credited in the release notes unless you prefer to remain anonymous.

## Scope

The following areas are in scope for security reports:

| Area | Details |
| --- | --- |
| **API calls** | Open-Meteo weather API requests in `engine/weather.py` |
| **File I/O** | JSON match data parsing in `engine/parser.py` and `data_io/` |
| **Cache files** | Weather cache at `data/weather_cache.json` |
| **Dependencies** | Vulnerabilities in `pygame`, `matplotlib`, `pandas`, `requests` |

### Out of Scope

- Cricsheet data accuracy or integrity (upstream responsibility)
- Local-only Pygame rendering issues with no security impact
- Feature requests or general bugs (use [GitHub Issues](../../issues) instead)

## Best Practices for Contributors

- Never commit API keys, tokens, or secrets
- Validate and sanitize all external data inputs (JSON match files, API responses)
- Pin dependency versions in `requirements.txt`
- Use `requests` with timeouts and proper User-Agent headers (already enforced)

---

<div align="center">

**Thank you for helping keep IPL Viz secure** 🛡️

</div>
