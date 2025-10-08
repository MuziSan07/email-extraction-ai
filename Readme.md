# Email Business Info Extractor

AI-powered application to extract business information from emails using Groq AI and FastAPI.

## Features

- 🤖 AI-powered extraction using Groq's GPT-OSS-120B model
- 📧 Extract: Name, Title, Company, Email, Phone, Address, Website
- 💾 SQLite database storage
- 🎨 Beautiful web interface with Jinja2 templates
- 👨‍💼 Admin panel to view all extracted contacts
- 🗑️ Delete contacts from admin panel
- 🚀 Fast API endpoints

## Project Structure

```
project/
│
├── main.py                 # FastAPI application
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (create this)
├── business_contacts.db    # SQLite database (auto-created)
│
└── templates/
    ├── index.html         # Home page with email input
    ├── result.html        # Extraction results page
    └── admin.html         # Admin panel with all contacts
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

Get your Groq API key from: https://console.groq.com

### 3. Run the Application

```bash
python main.py
```

Or using uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Access the Application

- **Home Page**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/docs

## API Endpoints

### Web Interface
- `GET /` - Home page with email input form
- `POST /extract` - Extract and save business info (form submission)
- `GET /admin` - Admin panel showing all contacts

### REST API
- `POST /api/extract` - Extract business info (JSON)
  ```json
  {
    "email_content": "your email text here"
  }
  ```
- `DELETE /api/contact/{contact_id}` - Delete a contact

## Database Schema

```sql
contacts (
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
```

## Usage Example

1. Open http://localhost:8000
2. Paste an email containing business information
3. Click "Extract Information"
4. View the extracted data
5. Check all contacts in the Admin Panel

## Example Email Format

```
Hi there,

My name is Sarah Johnson and I'm the Marketing Director at GlobalTech Solutions.

You can reach me at:
Email: sarah.johnson@globaltech.com
Phone: +1 (555) 987-6543
Mobile: +1 (555) 123-9999

Our office is located at:
123 Business Park Drive, Suite 400
San Francisco, CA 94107

Check out our website: www.globaltech.com

Best regards,
Sarah
```

## Troubleshooting

**Issue: Import errors**
```bash
pip install --upgrade -r requirements.txt
```

**Issue: Database not created**
- The database is auto-created on first run
- Check file permissions in the directory

**Issue: Groq API errors**
- Verify your API key in `.env`
- Check API rate limits
- Ensure the model name is correct: `openai/gpt-oss-120b`

## Technologies Used

- **FastAPI** - Web framework
- **LangChain + Groq** - AI extraction
- **SQLite** - Database
- **Jinja2** - Template engine
- **Python 3.8+** - Programming language

## License

MIT License