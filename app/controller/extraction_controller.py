"""Routes for manual extraction and the admin panel."""

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from .. import config
from ..model import contact_repository
from ..model.extractor import extract_business_info
from ..model.schemas import BusinessInfo, EmailInput
from ..security import require_admin

router = APIRouter()
templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/extract", response_class=HTMLResponse)
async def extract_email(request: Request, email_content: str = Form(...)):
    email_content = email_content[: config.MAX_EMAIL_LENGTH]
    try:
        info = extract_business_info(email_content)
        contact_id = contact_repository.save_contact(info, email_content)
        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "info": info,
                "contact_id": contact_id,
                "success": True,
            },
        )
    except Exception as exc:  # noqa: BLE001 - surface the message to the UI
        return templates.TemplateResponse(
            "result.html",
            {"request": request, "error": str(exc), "success": False},
        )


@router.post("/api/extract", response_model=BusinessInfo)
async def api_extract(email_input: EmailInput):
    info = extract_business_info(email_input.email_content)
    contact_repository.save_contact(info, email_input.email_content)
    return info


@router.get(
    "/admin",
    response_class=HTMLResponse,
    dependencies=[Depends(require_admin)],
)
async def admin_panel(request: Request):
    contacts = contact_repository.get_all_contacts()
    return templates.TemplateResponse(
        "admin.html", {"request": request, "contacts": contacts}
    )


@router.delete(
    "/api/contact/{contact_id}",
    dependencies=[Depends(require_admin)],
)
async def delete_contact(contact_id: int):
    try:
        contact_repository.delete_contact(contact_id)
        return {"success": True, "message": "Contact deleted"}
    except Exception as exc:  # noqa: BLE001
        return {"success": False, "error": str(exc)}
