"""Gmail OAuth and inbox-extraction routes.

These routes are protected by :func:`require_admin` when admin credentials are
configured, since they expose a connected mailbox.
"""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .. import config
from ..model import contact_repository, gmail_service
from ..model.extractor import extract_business_info
from ..security import require_admin

router = APIRouter(dependencies=[Depends(require_admin)])
templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))


@router.get("/authorize")
async def authorize():
    if not gmail_service.credentials_exist():
        return HTMLResponse(
            f"<h3>{config.GOOGLE_CREDENTIALS_FILE} not found. Add your Google "
            "OAuth client secrets file to the project root.</h3>",
            status_code=400,
        )
    return RedirectResponse(gmail_service.build_authorization_url())


@router.get("/oauth2callback")
async def oauth2callback(code: str = None, error: str = None):
    if error:
        return HTMLResponse(f"<h3>OAuth error: {error}</h3>", status_code=400)
    if not code:
        return HTMLResponse(
            "<h3>Missing authorization code. Retry /authorize.</h3>",
            status_code=400,
        )
    try:
        gmail_service.exchange_code_for_token(code)
    except Exception as exc:  # noqa: BLE001
        return HTMLResponse(
            f"<h3>Failed to fetch token: {exc}</h3>", status_code=400
        )
    return RedirectResponse("/emails")


@router.get("/emails", response_class=HTMLResponse)
async def fetch_emails(request: Request):
    try:
        messages = gmail_service.fetch_recent_messages()
    except Exception as exc:  # noqa: BLE001
        return HTMLResponse(
            f"<h3>Error: {exc}</h3>"
            "<p>Visit <a href='/authorize'>/authorize</a> to connect Gmail.</p>",
            status_code=400,
        )

    processed = []
    for message in messages:
        body = message["body"]
        info = extract_business_info(body)
        contact_repository.save_contact(info, body)
        snippet = (body[:300] + "...") if len(body) > 300 else body
        processed.append(
            {
                "subject": message["subject"],
                "from": message["from"],
                "snippet": snippet,
                "info": info,
            }
        )

    return templates.TemplateResponse(
        "emails.html", {"request": request, "emails": processed}
    )
