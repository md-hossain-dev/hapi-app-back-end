import requests
import json
from google.oauth2 import service_account
from google.auth.transport.requests import Request

SERVICE_ACCOUNT_FILE = 'habiba-e39ad-07bd1098ca32.json'
FIREBASE_API_URL = 'https://fcm.googleapis.com/v1/projects/{project_id}/messages:send'
print('SERVICE_ACCOUNT_FILE',SERVICE_ACCOUNT_FILE)

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=["https://www.googleapis.com/auth/firebase.messaging"]
)

def send_firebase_notification(fcm_token, title, body):
    if not credentials.valid:
        credentials.refresh(Request())

    access_token = credentials.token

    message = {
        "message": {
            "token": fcm_token,
            "notification": {
                "title": title,
                "body": body
            }
        }
    }

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json',
    }

    project_id = "habiba-e39ad"
    
    response = requests.post(
        FIREBASE_API_URL.format(project_id=project_id),
        headers=headers,
        data=json.dumps(message)
    )

    return response.status_code, response.json()
