"""Gmail OAuth integration and message retrieval.

The Google client libraries are imported lazily inside the functions that use
them, so the core extraction application can run without the optional Gmail
dependencies installed.
"""

import base64
import os
import re
from html import unescape
from typing import List

from .. import config


def _apply_insecure_transport() -> None:
    """Permit plain HTTP during OAuth, for local development only."""
    if config.OAUTH_INSECURE_TRANSPORT:
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"


def credentials_exist() -> bool:
    return os.path.exists(config.GOOGLE_CREDENTIALS_FILE)


def _load_credentials():
    import google.oauth2.credentials

    if not os.path.exists(config.GOOGLE_TOKEN_FILE):
        return None
    return google.oauth2.credentials.Credentials.from_authorized_user_file(
        config.GOOGLE_TOKEN_FILE, config.GMAIL_SCOPES
    )


def _save_credentials(creds) -> None:
    with open(config.GOOGLE_TOKEN_FILE, "w", encoding="utf-8") as handle:
        handle.write(creds.to_json())


def build_authorization_url() -> str:
    """Return the Google consent-screen URL to redirect the user to."""
    import google_auth_oauthlib.flow

    _apply_insecure_transport()
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        config.GOOGLE_CREDENTIALS_FILE, scopes=config.GMAIL_SCOPES
    )
    flow.redirect_uri = config.OAUTH_REDIRECT_URI
    authorization_url, _state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    return authorization_url


def exchange_code_for_token(code: str) -> None:
    """Exchange an OAuth authorization code for stored credentials."""
    import google_auth_oauthlib.flow

    _apply_insecure_transport()
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        config.GOOGLE_CREDENTIALS_FILE, scopes=config.GMAIL_SCOPES
    )
    flow.redirect_uri = config.OAUTH_REDIRECT_URI
    flow.fetch_token(code=code)
    _save_credentials(flow.credentials)


def _ensure_valid_credentials():
    from google.auth.transport.requests import Request as GoogleRequest

    creds = _load_credentials()
    if not creds:
        raise RuntimeError("Not authorized. Visit /authorize to connect Gmail.")
    if creds.expired and creds.refresh_token:
        creds.refresh(GoogleRequest())
        _save_credentials(creds)
    return creds


def _get_service():
    import googleapiclient.discovery

    creds = _ensure_valid_credentials()
    return googleapiclient.discovery.build("gmail", "v1", credentials=creds)


def _html_to_text(html: str) -> str:
    """Naive HTML-to-text: drop scripts/styles/tags and unescape entities."""
    text = re.sub(r"(?is)<script.*?>.*?</script>", "", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", "", text)
    text = re.sub(r"(?s)<br\s*/?>", "\n", text)
    text = re.sub(r"(?s)<li\s*/?>", "\n - ", text)
    text = re.sub(r"<[^>]+>", "", text)
    return unescape(text)


def _extract_text_from_parts(parts) -> str:
    text = ""
    for part in parts:
        mime = part.get("mimeType", "")
        body = part.get("body", {})
        data = body.get("data")
        if mime == "text/plain" and data:
            text += base64.urlsafe_b64decode(data).decode("utf-8", "ignore")
        elif mime == "text/html" and data and not text:
            html = base64.urlsafe_b64decode(data).decode("utf-8", "ignore")
            text += _html_to_text(html)
        if part.get("parts"):
            text += _extract_text_from_parts(part["parts"])
    return text


def _get_message_body(msg_data: dict) -> str:
    payload = msg_data.get("payload", {})
    parts = payload.get("parts")
    if parts:
        body = _extract_text_from_parts(parts)
    else:
        data = payload.get("body", {}).get("data")
        if not data:
            return ""
        decoded = base64.urlsafe_b64decode(data).decode("utf-8", "ignore")
        body = _html_to_text(decoded) if re.search(r"<[^>]+>", decoded) else decoded
    return body.strip()


def fetch_recent_messages() -> List[dict]:
    """Fetch recent inbox messages with their decoded bodies."""
    service = _get_service()
    results = (
        service.users()
        .messages()
        .list(userId="me", maxResults=config.GMAIL_MAX_RESULTS, labelIds=["INBOX"])
        .execute()
    )
    messages = results.get("messages", [])

    out = []
    for msg in messages:
        msg_data = (
            service.users()
            .messages()
            .get(userId="me", id=msg["id"], format="full")
            .execute()
        )
        headers = msg_data.get("payload", {}).get("headers", [])
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "")
        body = _get_message_body(msg_data) or msg_data.get("snippet", "")
        out.append({"subject": subject, "from": sender, "body": body})
    return out
