# AGENTS

- Do not version or expose internal campaign data, especially `assets/Abbinamenti DEF.xlsx` or any real appointment list.
- Use synthetic test fixtures for all automated validation.
- Keep the user-facing workflow simple and safe for non-technical Windows users.
- Preserve language and output cleanly in Italian when it matches the user request.
- Prefer small, testable modules and keep the repository buildable on Linux for technical validation.
- If a test fails, fix the root cause and rerun the relevant tests before moving on.
- Treat the final release as a Windows `.exe` distribution with a clear help/guide PDF.
- If there is any doubt about requirements or behavior, ask the user before acting.
- For every requested implementation, run the relevant tests and do not consider
  the task complete until all tests pass successfully.
- At the end of an implementation, push the changes and publish the release.
- Never send private data from files under `assets/` to the LLM; use synthetic
  fixtures and privacy-safe structural checks instead.
