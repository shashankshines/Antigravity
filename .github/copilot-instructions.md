## Quick orientation

This repository is a small Streamlit app called "AI Email Agent" that generates and (optionally) sends emails using Google's Generative AI (Gemini) and optional SMTP. Key entry points:
- `app.py` — Streamlit UI and state persistence. The front-end controls theme, subject input, attachments, and sends requests to `EmailAgent`.
- `email_agent.py` — Core agent: configures the `google-generativeai` client, builds prompts, generates email body/subjects, validates placeholders, and handles (mock or real) sending via SMTP.
- `test_agent.py`, `test_smtp.py` — unit/diagnostic scripts demonstrating how the agent is initialized and how SMTP is tested.
- `.agent/workflows/streamlit-deployment.md`, `DEPLOYMENT.md` — deployment notes for Streamlit Cloud and manual steps.

## What matters for edits

- API key: the Gemini key is read from `GEMINI_API_KEY` (env / `.streamlit/secrets.toml` in Streamlit Cloud). If missing the agent falls back to mock behavior. Search for `GEMINI_API_KEY` and `genai.configure` in `email_agent.py` when changing generation logic.
- Mock vs real send: `EmailAgent(mock_mode=True)` prints the email to stdout; `mock_mode=False` triggers SMTP code paths. Tests rely on mock mode.
- Prompt contracts: Prompts constructed in `generate_email` and `optimize_subject` expect the model response in `response.text`. Post-processing strips an optional leading "Subject:" line. If you change prompt/response parsing, update tests accordingly.
- Persistence: `app.py` uses `st.session_state` and `st.query_params` for persisting `api_key`, `smtp_*`, `signature`, `theme`, etc. Keep changes compatible with that pattern to preserve UX behavior.

## Common tasks & commands

- Run app locally (requires deps in `requirements.txt`, set GEMINI_API_KEY if you want generation):
  - Install: `pip install -r requirements.txt`
  - Run: `streamlit run app.py`
- Run unit tests:
  - `python -m unittest test_agent.py`
- Test SMTP (diagnostic):
  - `python test_smtp.py --email you@example.com --password <app-password> --to you@example.com`

## Patterns & conventions

- Small, focused modules: UI logic stays in `app.py`, generation and sending logic in `email_agent.py`. Prefer adding helper functions to `email_agent.py` for shared logic (subject formatting, placeholder detection).
- Minimal dependencies: `google-generativeai`, `streamlit`, `streamlit-quill`, `python-dotenv`. Avoid adding heavy frameworks without explicit need.
- Environment-first config: secrets are read from env vars / `.streamlit/secrets.toml` on deploy. Do not hardcode API keys.
- Tests assume mocked generation or patched `genai.GenerativeModel`. When modifying generation call-sites, update `test_agent.py` mocks.

## Integration notes

- Gemini usage: `email_agent.py` calls `genai.GenerativeModel('gemini-2.0-flash')` and `generate_content`. If the API shape changes, update formation and tests. The repo also includes `list_models.py` as a quick utility to list available models.
- SMTP: the SMTP sender uses `smtplib` and MIME classes in `email_agent.py` and `test_smtp.py`. Port and TLS usage (starttls) are assumed; modify carefully.
- Streamlit Cloud: `.agent/workflows/streamlit-deployment.md` documents automatic and manual deployments. The app uses `requirements.txt` and `.streamlit/secrets.toml` for env vars.

## Examples to copy/paste

- Initialize agent for local testing (mock):

  from email_agent import EmailAgent
  agent = EmailAgent(api_key='fake', mock_mode=True)

- Generate an email body (production):

  agent = EmailAgent(api_key=os.getenv('GEMINI_API_KEY'), mock_mode=False)
  body = agent.generate_email('Invoice for March')

## When to ask for guidance

- If you need to change prompt structure, run `python -m unittest test_agent.py` and update mocks. Also check `app.py` for UI expectations (placeholder and attachment handling).
- If changing how secrets are loaded, update `.agent/workflows/streamlit-deployment.md` and note Streamlit Cloud secret names.

If anything here is unclear or you'd like me to expand a section (for example, add example unit tests or CI steps), tell me which area and I'll iterate.
