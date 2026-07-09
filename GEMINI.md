# Gemini CLI Instructions

Gemini CLI should use this file as the day-to-day context entrypoint for this project.

@./AGENTS.md

If imports are unavailable in the current Gemini CLI version, read `AGENTS.md` directly before substantial work.

Gemini-specific caution: verify the active auth route before running agent work. Do not assume Google sign-in, API key, or Vertex credentials are free or interchangeable. Check for `GOOGLE_API_KEY`, `GEMINI_API_KEY`, and `GOOGLE_APPLICATION_CREDENTIALS` by presence only; never print secret values.
