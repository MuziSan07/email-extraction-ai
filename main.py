# from fastapi import FastAPI, Request, Form
# from fastapi.responses import HTMLResponse, JSONResponse
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
# from langchain_groq import ChatGroq
# from langchain.prompts import PromptTemplate
# from pydantic import BaseModel
# import sqlite3
# import os
# import json
# from dotenv import load_dotenv
# from datetime import datetime

# load_dotenv()

# app = FastAPI(title="Email Business Info Extractor")
# templates = Jinja2Templates(directory="templates")

# # Initialize Groq LLM
# llm = ChatGroq(
#     model="openai/gpt-oss-120b",
#     api_key=os.getenv("GROQ_API_KEY"),
#     temperature=0
# )

# # Database initialization
# def init_db():
#     conn = sqlite3.connect('business_contacts.db')
#     c = conn.cursor()
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS contacts (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT,
#             title TEXT,
#             company TEXT,
#             email TEXT,
#             phone TEXT,
#             address TEXT,
#             website TEXT,
#             other_info TEXT,
#             extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             raw_email TEXT
#         )
#     ''')
#     conn.commit()
#     conn.close()

# init_db()

# # Pydantic models
# class EmailInput(BaseModel):
#     email_content: str

# class BusinessInfo(BaseModel):
#     name: str = ""
#     title: str = ""
#     company: str = ""
#     email: str = ""
#     phone: str = ""
#     address: str = ""
#     website: str = ""
#     other_info: str = ""

# # Extraction prompt template
# extraction_prompt = PromptTemplate(
#     input_variables=["email_content"],
#     template="""
# You are an AI assistant that extracts business information from emails. 
# Extract the following information from the email content and return ONLY a valid JSON object with these exact keys:

# - name: Full name or username of the person
# - title: Job title or designation
# - company: Company or group name
# - email: Email address
# - phone: Phone number(s) - if multiple, separate with commas
# - address: Physical address
# - website: Website URL
# - other_info: Any other important information (use bullet points with • separator if multiple items)

# If any information is not found, use an empty string "".

# Email Content:
# {email_content}

# Return ONLY the JSON object, no other text:
# """
# )

# def extract_business_info(email_content: str) -> BusinessInfo:
#     """Extract business information from email using Groq AI"""
#     try:
#         prompt = extraction_prompt.format(email_content=email_content)
#         response = llm.invoke(prompt)
        
#         # Parse the response
#         content = response.content.strip()
        
#         # Try to extract JSON from response
#         if "```json" in content:
#             content = content.split("```json")[1].split("```")[0].strip()
#         elif "```" in content:
#             content = content.split("```")[1].split("```")[0].strip()
        
#         data = json.loads(content)
#         return BusinessInfo(**data)
#     except Exception as e:
#         print(f"Error extracting info: {e}")
#         return BusinessInfo()

# def save_to_db(info: BusinessInfo, raw_email: str):
#     """Save extracted info to SQLite database"""
#     conn = sqlite3.connect('business_contacts.db')
#     c = conn.cursor()
#     c.execute('''
#         INSERT INTO contacts 
#         (name, title, company, email, phone, address, website, other_info, raw_email)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#     ''', (
#         info.name, info.title, info.company, info.email, 
#         info.phone, info.address, info.website, info.other_info, raw_email
#     ))
#     conn.commit()
#     contact_id = c.lastrowid
#     conn.close()
#     return contact_id

# def get_all_contacts():
#     """Retrieve all contacts from database"""
#     conn = sqlite3.connect('business_contacts.db')
#     c = conn.cursor()
#     c.execute('SELECT * FROM contacts ORDER BY extracted_at DESC')
#     contacts = c.fetchall()
#     conn.close()
#     return contacts

# # API Endpoints
# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     """Home page with email input form"""
#     return templates.TemplateResponse("index.html", {"request": request})

# @app.post("/extract", response_class=HTMLResponse)
# async def extract_email(request: Request, email_content: str = Form(...)):
#     """Extract business info from email and save to database"""
#     try:
#         # Extract information
#         info = extract_business_info(email_content)
        
#         # Save to database
#         contact_id = save_to_db(info, email_content)
        
#         return templates.TemplateResponse("result.html", {
#             "request": request,
#             "info": info,
#             "contact_id": contact_id,
#             "success": True
#         })
#     except Exception as e:
#         return templates.TemplateResponse("result.html", {
#             "request": request,
#             "error": str(e),
#             "success": False
#         })

# @app.post("/api/extract", response_model=BusinessInfo)
# async def api_extract(email_input: EmailInput):
#     """API endpoint for extracting business info"""
#     info = extract_business_info(email_input.email_content)
#     save_to_db(info, email_input.email_content)
#     return info

# @app.get("/admin", response_class=HTMLResponse)
# async def admin_panel(request: Request):
#     """Admin panel to view all extracted contacts"""
#     contacts = get_all_contacts()
#     return templates.TemplateResponse("admin.html", {
#         "request": request,
#         "contacts": contacts
#     })

# @app.delete("/api/contact/{contact_id}")
# async def delete_contact(contact_id: int):
#     """Delete a contact from database"""
#     try:
#         conn = sqlite3.connect('business_contacts.db')
#         c = conn.cursor()
#         c.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
#         conn.commit()
#         conn.close()
#         return {"success": True, "message": "Contact deleted"}
#     except Exception as e:
#         return {"success": False, "error": str(e)}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

# from fastapi import FastAPI, Request, Form
# from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
# from fastapi.templating import Jinja2Templates
# from fastapi.staticfiles import StaticFiles
# from pydantic import BaseModel
# from langchain_groq import ChatGroq
# from langchain.prompts import PromptTemplate
# import sqlite3
# import os
# import json
# from dotenv import load_dotenv
# from datetime import datetime

# # Gmail API imports
# import google.oauth2.credentials
# import google_auth_oauthlib.flow
# import googleapiclient.discovery

# # -------------------------------------------------------------------
# # Environment + Config
# # -------------------------------------------------------------------
# os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # Allow HTTP locally
# load_dotenv()

# app = FastAPI(title="Email Business Info Extractor")
# templates = Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"), name="static")

# # -------------------------------------------------------------------
# # Initialize Groq LLM
# # -------------------------------------------------------------------
# llm = ChatGroq(
#     model="openai/gpt-oss-120b",
#     api_key=os.getenv("GROQ_API_KEY"),
#     temperature=0
# )

# # -------------------------------------------------------------------
# # Gmail API setup
# # -------------------------------------------------------------------
# SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
# CREDENTIALS_FILE = "credentials.json"

# # -------------------------------------------------------------------
# # Database initialization
# # -------------------------------------------------------------------
# def init_db():
#     conn = sqlite3.connect('business_contacts.db')
#     c = conn.cursor()
#     c.execute('''
#         CREATE TABLE IF NOT EXISTS contacts (
#             id INTEGER PRIMARY KEY AUTOINCREMENT,
#             name TEXT,
#             title TEXT,
#             company TEXT,
#             email TEXT,
#             phone TEXT,
#             address TEXT,
#             website TEXT,
#             other_info TEXT,
#             extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#             raw_email TEXT
#         )
#     ''')
#     conn.commit()
#     conn.close()

# init_db()

# # -------------------------------------------------------------------
# # Pydantic Models
# # -------------------------------------------------------------------
# class EmailInput(BaseModel):
#     email_content: str

# class BusinessInfo(BaseModel):
#     name: str = ""
#     title: str = ""
#     company: str = ""
#     email: str = ""
#     phone: str = ""
#     address: str = ""
#     website: str = ""
#     other_info: str = ""

# # -------------------------------------------------------------------
# # Prompt Template
# # -------------------------------------------------------------------
# extraction_prompt = PromptTemplate(
#     input_variables=["email_content"],
#     template="""
# You are an AI assistant that extracts business information from emails.
# Extract and return ONLY a valid JSON object with these exact keys:
# - name
# - title
# - company
# - email
# - phone
# - address
# - website
# - other_info

# Email Content:
# {email_content}

# Return ONLY the JSON object, no other text.
# """
# )

# # -------------------------------------------------------------------
# # Business Info Extraction Logic
# # -------------------------------------------------------------------
# def extract_business_info(email_content: str) -> BusinessInfo:
#     try:
#         prompt = extraction_prompt.format(email_content=email_content)
#         response = llm.invoke(prompt)
#         content = response.content.strip()

#         if "```json" in content:
#             content = content.split("```json")[1].split("```")[0].strip()
#         elif "```" in content:
#             content = content.split("```")[1].split("```")[0].strip()

#         data = json.loads(content)
#         return BusinessInfo(**data)
#     except Exception as e:
#         print(f"Error extracting info: {e}")
#         return BusinessInfo()

# def save_to_db(info: BusinessInfo, raw_email: str):
#     conn = sqlite3.connect('business_contacts.db')
#     c = conn.cursor()
#     c.execute('''
#         INSERT INTO contacts 
#         (name, title, company, email, phone, address, website, other_info, raw_email)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
#     ''', (
#         info.name, info.title, info.company, info.email,
#         info.phone, info.address, info.website, info.other_info, raw_email
#     ))
#     conn.commit()
#     contact_id = c.lastrowid
#     conn.close()
#     return contact_id

# def get_all_contacts():
#     conn = sqlite3.connect('business_contacts.db')
#     c = conn.cursor()
#     c.execute('SELECT * FROM contacts ORDER BY extracted_at DESC')
#     contacts = c.fetchall()
#     conn.close()
#     return contacts

# # -------------------------------------------------------------------
# # Gmail Fetch Function
# # -------------------------------------------------------------------
# def get_gmail_service():
#     """Create a Gmail API service instance using OAuth2 credentials"""
#     if not os.path.exists('token.json'):
#         raise Exception("You must authorize first via /authorize endpoint")

#     creds = google.oauth2.credentials.Credentials.from_authorized_user_file('token.json', SCOPES)
#     service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)
#     return service

# # -------------------------------------------------------------------
# # Routes
# # -------------------------------------------------------------------
# @app.get("/", response_class=HTMLResponse)
# async def home(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# @app.post("/extract", response_class=HTMLResponse)
# async def extract_email(request: Request, email_content: str = Form(...)):
#     info = extract_business_info(email_content)
#     contact_id = save_to_db(info, email_content)
#     return templates.TemplateResponse("result.html", {
#         "request": request,
#         "info": info,
#         "contact_id": contact_id,
#         "success": True
#     })

# @app.post("/api/extract", response_model=BusinessInfo)
# async def api_extract(email_input: EmailInput):
#     info = extract_business_info(email_input.email_content)
#     save_to_db(info, email_input.email_content)
#     return info

# @app.get("/admin", response_class=HTMLResponse)
# async def admin_panel(request: Request):
#     contacts = get_all_contacts()
#     return templates.TemplateResponse("admin.html", {"request": request, "contacts": contacts})

# @app.delete("/api/contact/{contact_id}")
# async def delete_contact(contact_id: int):
#     try:
#         conn = sqlite3.connect('business_contacts.db')
#         c = conn.cursor()
#         c.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
#         conn.commit()
#         conn.close()
#         return {"success": True, "message": "Contact deleted"}
#     except Exception as e:
#         return {"success": False, "error": str(e)}

# # -------------------------------------------------------------------
# # Gmail Integration Endpoints
# # -------------------------------------------------------------------
# @app.get("/authorize")
# async def authorize():
#     flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
#         CREDENTIALS_FILE, scopes=SCOPES)
#     flow.redirect_uri = "http://localhost:8000/oauth2callback"

#     authorization_url, state = flow.authorization_url(
#         access_type='offline',
#         include_granted_scopes='true')
#     return RedirectResponse(authorization_url)

# @app.get("/oauth2callback")
# async def oauth2callback(code: str):
#     flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
#         CREDENTIALS_FILE, scopes=SCOPES)
#     flow.redirect_uri = "http://localhost:8000/oauth2callback"

#     flow.fetch_token(code=code)
#     creds = flow.credentials

#     # Save token
#     with open('token.json', 'w') as token:
#         token.write(creds.to_json())

#     return RedirectResponse("/emails")

# @app.get("/emails", response_class=HTMLResponse)
# async def fetch_emails(request: Request):
#     """Fetch latest Gmail messages and extract info using Groq AI"""
#     try:
#         service = get_gmail_service()
#         results = service.users().messages().list(userId='me', maxResults=5, labelIds=['INBOX']).execute()
#         messages = results.get('messages', [])

#         processed = []
#         for msg in messages:
#             msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
#             snippet = msg_data.get('snippet', '')
#             info = extract_business_info(snippet)
#             save_to_db(info, snippet)
#             processed.append({
#                 "subject": next((h['value'] for h in msg_data['payload']['headers'] if h['name'] == 'Subject'), ""),
#                 "from": next((h['value'] for h in msg_data['payload']['headers'] if h['name'] == 'From'), ""),
#                 "snippet": snippet,
#                 "info": info
#             })

#         return templates.TemplateResponse("email.html", {"request": request, "emails": processed})
#     except Exception as e:
#         return HTMLResponse(f"<h3>Error: {e}</h3>")

# # -------------------------------------------------------------------
# # Run app
# # -------------------------------------------------------------------
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)



# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from langchain_groq import ChatGroq
from langchain.prompts import PromptTemplate
import sqlite3
import os
import json
from dotenv import load_dotenv
from datetime import datetime
import base64
import re
from html import unescape

# Gmail API imports
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.auth.transport.requests import Request as GoogleRequest

# -------------------------------------------------------------------
# Environment + Config
# -------------------------------------------------------------------
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'  # local dev allow http
load_dotenv()

app = FastAPI(title="Email Business Info Extractor")
templates = Jinja2Templates(directory="templates")
if not os.path.exists("static"):
    os.makedirs("static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# -------------------------------------------------------------------
# Initialize Groq LLM
# -------------------------------------------------------------------
llm = ChatGroq(
    model="openai/gpt-oss-120b",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0
)

# -------------------------------------------------------------------
# Gmail API setup
# -------------------------------------------------------------------
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"

# -------------------------------------------------------------------
# Database initialization
# -------------------------------------------------------------------
def init_db():
    conn = sqlite3.connect('business_contacts.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            title TEXT,
            company TEXT,
            email TEXT,
            phone TEXT,
            address TEXT,
            website TEXT,
            other_info TEXT,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            raw_email TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# -------------------------------------------------------------------
# Pydantic Models
# -------------------------------------------------------------------
class EmailInput(BaseModel):
    email_content: str

class BusinessInfo(BaseModel):
    name: str = ""
    title: str = ""
    company: str = ""
    email: str = ""
    phone: str = ""
    address: str = ""
    website: str = ""
    other_info: str = ""

# -------------------------------------------------------------------
# Prompt Template (clear instructions)
# -------------------------------------------------------------------
extraction_prompt = PromptTemplate(
    input_variables=["email_content"],
    template="""
You are an assistant that MUST extract clean, accurate business contact information from the FULL EMAIL BODY provided.

Read the entire email body and return ONLY a single valid JSON object with these exact keys (use empty string "" when data not present):

- name
- title
- company
- email
- phone
- address
- website
- other_info

Rules:
- Return ONLY the JSON object and nothing else.
- Combine multiple phone numbers with a comma and space.
- Normalize website to include http:// or https:// if missing.
- other_info should include short bullet-like facts separated by " • " (for example: "• Department: OnTrack Event • Part of Rudskogen Motorsenter AS").
- Use values only from the email body (signature, footer, headers inside body). Do not invent or fetch external data.

Email Body:
{email_content}

Return ONLY the JSON object.
"""
)

# -------------------------------------------------------------------
# Extraction and DB logic
# -------------------------------------------------------------------
def extract_business_info(email_content: str) -> BusinessInfo:
    """Call the LLM to extract structured info from the full email body."""
    try:
        prompt = extraction_prompt.format(email_content=email_content)
        response = llm.invoke(prompt)
        content = response.content.strip()

        # If model wrapped JSON in code fences, extract inner JSON
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        # Safely load JSON
        data = json.loads(content)
        return BusinessInfo(**data)
    except Exception as e:
        # Log for debug and return empty structure
        print("Error extracting info:", e)
        return BusinessInfo()

def save_to_db(info: BusinessInfo, raw_email: str):
    conn = sqlite3.connect('business_contacts.db')
    c = conn.cursor()
    c.execute('''
        INSERT INTO contacts 
        (name, title, company, email, phone, address, website, other_info, raw_email)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        info.name, info.title, info.company, info.email,
        info.phone, info.address, info.website, info.other_info, raw_email
    ))
    conn.commit()
    contact_id = c.lastrowid
    conn.close()
    return contact_id

def get_all_contacts():
    conn = sqlite3.connect('business_contacts.db')
    c = conn.cursor()
    c.execute('SELECT * FROM contacts ORDER BY extracted_at DESC')
    contacts = c.fetchall()
    conn.close()
    return contacts

# -------------------------------------------------------------------
# Gmail helpers
# -------------------------------------------------------------------
def load_credentials_from_token():
    if not os.path.exists(TOKEN_FILE):
        return None
    creds = google.oauth2.credentials.Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return creds

def save_credentials_to_token(creds):
    with open(TOKEN_FILE, 'w') as f:
        f.write(creds.to_json())

def ensure_valid_credentials():
    creds = load_credentials_from_token()
    if not creds:
        raise Exception("You must authorize first via /authorize endpoint")
    # refresh if expired and refresh_token available
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(GoogleRequest())
            save_credentials_to_token(creds)
        except Exception as e:
            # token refresh failed
            print("Failed to refresh token:", e)
            raise Exception("Failed to refresh token; please re-authorize via /authorize")
    return creds

def get_gmail_service():
    """Create a Gmail API service instance using OAuth2 credentials"""
    creds = ensure_valid_credentials()
    service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)
    return service

def _extract_plain_text_from_parts(parts):
    text = ""
    for part in parts:
        mime = part.get('mimeType', '')
        body = part.get('body', {})
        if mime == 'text/plain' and body.get('data'):
            data = body.get('data')
            text += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        elif mime == 'text/html' and body.get('data') and not text:
            # if no text/plain found yet, capture html to convert later
            data = body.get('data')
            html = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            # simple html->text fallback
            text += html_to_text(html)
        # nested parts
        if part.get('parts'):
            text += _extract_plain_text_from_parts(part.get('parts'))
    return text

def html_to_text(html: str) -> str:
    # naive HTML -> text: remove tags, unescape entities
    text = re.sub(r'(?is)<script.*?>.*?</script>', '', html)
    text = re.sub(r'(?is)<style.*?>.*?</style>', '', text)
    text = re.sub(r'(?s)<br\s*/?>', '\n', text)
    text = re.sub(r'(?s)<li\s*/?>', '\n - ', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    return text

def get_full_message_text(msg_data: dict) -> str:
    """Return the decoded full message body (prefers text/plain but falls back to html)"""
    payload = msg_data.get('payload', {})
    parts = payload.get('parts')
    full_text = ""
    if parts:
        full_text = _extract_plain_text_from_parts(parts)
    else:
        # single-part message, check body directly
        body = payload.get('body', {})
        data = body.get('data')
        if data:
            decoded = base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
            # if looks like html, convert
            if bool(re.search(r'<[^>]+>', decoded)):
                full_text = html_to_text(decoded)
            else:
                full_text = decoded
    # final cleanup
    full_text = full_text.strip()
    return full_text

# -------------------------------------------------------------------
# Routes
# -------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/extract", response_class=HTMLResponse)
async def extract_email(request: Request, email_content: str = Form(...)):
    info = extract_business_info(email_content)
    contact_id = save_to_db(info, email_content)
    return templates.TemplateResponse("result.html", {
        "request": request,
        "info": info,
        "contact_id": contact_id,
        "success": True
    })

@app.post("/api/extract", response_model=BusinessInfo)
async def api_extract(email_input: EmailInput):
    info = extract_business_info(email_input.email_content)
    save_to_db(info, email_input.email_content)
    return info

@app.get("/admin", response_class=HTMLResponse)
async def admin_panel(request: Request):
    contacts = get_all_contacts()
    return templates.TemplateResponse("admin.html", {"request": request, "contacts": contacts})

@app.delete("/api/contact/{contact_id}")
async def delete_contact(contact_id: int):
    try:
        conn = sqlite3.connect('business_contacts.db')
        c = conn.cursor()
        c.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
        conn.commit()
        conn.close()
        return {"success": True, "message": "Contact deleted"}
    except Exception as e:
        return {"success": False, "error": str(e)}

# -------------------------------------------------------------------
# Gmail Integration Endpoints
# -------------------------------------------------------------------
@app.get("/authorize")
async def authorize():
    """
    Starts OAuth2 authorization. User should visit this URL to authorize Gmail access.
    Redirect URI configured in Google Console must be: http://localhost:8000/oauth2callback
    """
    if not os.path.exists(CREDENTIALS_FILE):
        return HTMLResponse("<h3>credentials.json not found. Upload credentials.json to the project folder.</h3>")

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CREDENTIALS_FILE, scopes=SCOPES)
    flow.redirect_uri = "http://localhost:8000/oauth2callback"

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'  # ask refresh token every time for robustness
    )
    # store state in a simple server-side temporary file (stateless across requests)
    # for simplicity we don't persist state between requests here because Flow.fetch_token with code only works
    return RedirectResponse(authorization_url)

@app.get("/oauth2callback")
async def oauth2callback(code: str = None, error: str = None):
    """
    OAuth2 callback. Google will redirect here with ?code=... (or error).
    """
    if error:
        return HTMLResponse(f"<h3>OAuth Error: {error}</h3>")

    if not code:
        return HTMLResponse("<h3>Missing code parameter from Google. Please retry /authorize</h3>")

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CREDENTIALS_FILE, scopes=SCOPES)
    flow.redirect_uri = "http://localhost:8000/oauth2callback"

    # Exchange code for tokens
    try:
        flow.fetch_token(code=code)
    except Exception as e:
        return HTMLResponse(f"<h3>Failed to fetch token: {e}</h3>")

    creds = flow.credentials
    # Save token for future requests
    save_credentials_to_token(creds)
    return RedirectResponse("/emails")

@app.get("/emails", response_class=HTMLResponse)
async def fetch_emails(request: Request):
    """Fetch latest Gmail messages, extract full body, call LLM, save results and display them."""
    try:
        service = get_gmail_service()
    except Exception as e:
        return HTMLResponse(f"<h3>Error: {e}</h3><p>Visit <a href='/authorize'>/authorize</a> to connect your Gmail account.</p>")

    try:
        results = service.users().messages().list(userId='me', maxResults=10, labelIds=['INBOX']).execute()
        messages = results.get('messages', [])

        processed = []
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
            subject = next((h['value'] for h in msg_data.get('payload', {}).get('headers', []) if h['name'] == 'Subject'), "")
            frm = next((h['value'] for h in msg_data.get('payload', {}).get('headers', []) if h['name'] == 'From'), "")
            # get full decoded email body
            full_body = get_full_message_text(msg_data)
            # if empty, fallback to snippet
            if not full_body:
                full_body = msg_data.get('snippet', '')

            # Extract with LLM using full body
            info = extract_business_info(full_body)
            # Save into DB
            save_to_db(info, full_body)

            processed.append({
                "subject": subject,
                "from": frm,
                "snippet": (full_body[:300] + "...") if len(full_body) > 300 else full_body,
                "info": info
            })

        return templates.TemplateResponse("email.html", {"request": request, "emails": processed})
    except Exception as e:
        return HTMLResponse(f"<h3>Error fetching emails: {e}</h3>")

# -------------------------------------------------------------------
# Run app
# -------------------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
