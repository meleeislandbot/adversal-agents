# Security Policy

## Scope

This repository is for authorized AI-agent red-team research and defensive evaluation.

## Report a vulnerability

Open a GitHub issue if the report is non-sensitive. For sensitive reports, contact the maintainers privately before publishing exploit details.

## Safety boundaries

Do not use this project to perform unauthorized intrusion, credential theft, malware deployment, harassment, production abuse, or evasion of provider limits.

## Secret handling

- Never commit secrets.
- Never print secret values in logs or diagnostics.
- Check environment-variable presence by name only.
- Treat API-key routes as cost-sensitive until explicitly approved.
