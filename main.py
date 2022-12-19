import os.path
# Google
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from time import sleep
from threading import Thread

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def main():
    credentials = None
    if os.path.exists("token.json"):
        credentials = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            credentials.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            credentials = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(credentials.to_json())

    # Do the above, but in a thread.
    t = Thread(target=check_for_unread, args=(credentials,))
    t.start()

def check_for_unread(credentials):
    listen = True
    while listen:
        service = build("gmail", "v1", credentials=credentials)
        # Get the user's unread emails
        results = service.users().messages().list(userId="me", labelIds=["UNREAD"]).execute()
        messages = results.get("messages", [])
        if not messages:
            print(f"{datetime.now().strftime('%H:%M:%S')} No unread emails")
        else:
            os.system(f"osascript -e 'tell app \"System Events\" to display dialog \"Unread emails: {len(messages)}\"'")
            listen = False

        sleep(15)


if __name__ == "__main__":
    main()
