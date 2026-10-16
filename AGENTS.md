# AGENTS

- Do not version or expose internal campaign data, especially `assets/Abbinamenti DEF.xlsx` or any real appointment list.
- Use synthetic test fixtures for all automated validation.
- Keep the user-facing workflow simple and safe for non-technical Windows users.
- Preserve language and output cleanly in Italian when it matches the user request.
- Prefer small, testable modules and keep the repository buildable on Linux for technical validation.
- If a test fails, fix the root cause and rerun the relevant tests before moving on.
- Treat the final release as a Windows `.exe` distribution with a clear help/guide PDF.
