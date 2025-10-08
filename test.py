from flask import Flask, redirect, url_for, session, request, render_template_string
import os
import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

# -------------------------------------------------------------------
# ✅ FIX for local testing (allows HTTP during OAuth)
# -------------------------------------------------------------------
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# -------------------------------------------------------------------
# Flask App Setup
# -------------------------------------------------------------------
app = Flask(__name__)
app.secret_key = "replace_with_a_random_secret_key"

# Gmail API scope (read-only access)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# -------------------------------------------------------------------
# Index Route - Displays latest emails
# -------------------------------------------------------------------
@app.route('/')
def index():
    if 'credentials' not in session:
        return redirect('authorize')

    creds = google.oauth2.credentials.Credentials(**session['credentials'])
    service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)

    # Fetch the latest 10 inbox messages
    results = service.users().messages().list(userId='me', maxResults=10, labelIds=['INBOX']).execute()
    messages = results.get('messages', [])

    emails = []
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id']).execute()
        headers = msg_data['payload']['headers']

        subject = sender = date = "(unknown)"
        for h in headers:
            if h['name'] == 'Subject': subject = h['value']
            elif h['name'] == 'From': sender = h['value']
            elif h['name'] == 'Date': date = h['value']

        snippet = msg_data.get('snippet', '')
        emails.append({
            'subject': subject,
            'from': sender,
            'date': date,
            'snippet': snippet
        })

    # Refresh credentials in session (keeps you logged in)
    session['credentials'] = creds_to_dict(creds)

    # -------------------------------------------------------------------
    # Simple HTML Template (dark mode)
    # -------------------------------------------------------------------
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>📨 Gmail Inbox</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #121212; color: #eee; padding: 30px; }
            h1 { color: #00bcd4; }
            .email { border-bottom: 1px solid #333; padding: 10px 0; }
            .subject { font-size: 16px; color: #ffeb3b; font-weight: bold; }
            .from { color: #03a9f4; margin-top: 4px; }
            .date { font-size: 13px; color: #999; }
            .snippet { font-size: 14px; color: #ccc; margin-top: 4px; }
            a { color: #00bcd4; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>📬 Latest Gmail Messages</h1>
        {% for e in emails %}
            <div class="email">
                <div class="subject">📧 {{ e.subject }}</div>
                <div class="from">From: {{ e.from }}</div>
                <div class="date">Date: {{ e.date }}</div>
                <div class="snippet">{{ e.snippet }}</div>
            </div>
        {% endfor %}
        <p><a href="/logout">Logout</a></p>
    </body>
    </html>
    '''
    return render_template_string(html, emails=emails)

# -------------------------------------------------------------------
# Step 1: Google OAuth Authorization
# -------------------------------------------------------------------
@app.route('/authorize')
def authorize():
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'credentials.json', scopes=SCOPES)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    session['state'] = state
    return redirect(authorization_url)

# -------------------------------------------------------------------
# Step 2: OAuth Callback Handler
# -------------------------------------------------------------------
@app.route('/oauth2callback')
def oauth2callback():
    state = session['state']
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'credentials.json', scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    authorization_response = request.url
    flow.fetch_token(authorization_response=authorization_response)

    creds = flow.credentials
    session['credentials'] = creds_to_dict(creds)

    return redirect(url_for('index'))

# -------------------------------------------------------------------
# Logout / Clear Session
# -------------------------------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# -------------------------------------------------------------------
# Helper Function
# -------------------------------------------------------------------
def creds_to_dict(creds):
    return {
        'token': creds.token,
        'refresh_token': creds.refresh_token,
        'token_uri': creds.token_uri,
        'client_id': creds.client_id,
        'client_secret': creds.client_secret,
        'scopes': creds.scopes
    }

# -------------------------------------------------------------------
# Run App
# -------------------------------------------------------------------
if __name__ == '__main__':
    print("🚀 Starting Gmail Inbox Viewer on http://localhost:8080")
    app.run('localhost', 8080, debug=True)
