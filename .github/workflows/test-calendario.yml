import os
import requests
import datetime
from zoneinfo import ZoneInfo
from msal import ConfidentialClientApplication
from dateutil import parser

# Configura fuso orario italiano
italy_tz = ZoneInfo("Europe/Rome")
now = datetime.datetime.now(italy_tz)
end_time = now + datetime.timedelta(hours=2)

# Parametri da GitHub secrets
tenant_id = os.environ["AZURE_TENANT_ID"]
client_id = os.environ["AZURE_CLIENT_ID"]
client_secret = os.environ["AZURE_CLIENT_SECRET"]

authority = f"https://login.microsoftonline.com/{tenant_id}"
scope = ["https://graph.microsoft.com/.default"]

# ID della risorsa condivisa (sala riunioni)
room_email = "salariunioni@etgrisorse.com"

# Ottieni token di accesso con MSAL
app = ConfidentialClientApplication(client_id, authority=authority, client_credential=client_secret)
result = app.acquire_token_for_client(scopes=scope)

if "access_token" not in result:
    print("Errore durante l'autenticazione:", result.get("error_description"))
    exit(1)

# Imposta intestazioni per Graph API
headers = {
    "Authorization": f"Bearer {result['access_token']}",
    "Content-Type": "application/json"
}

# Intervallo temporale in formato ISO 8601
start_iso = now.isoformat()
end_iso = end_time.isoformat()

# Richiesta eventi al calendario della sala riunioni
url = f"https://graph.microsoft.com/v1.0/users/{room_email}/calendarview?startDateTime={start_iso}&endDateTime={end_iso}&$orderby=start/dateTime"

response = requests.get(url, headers=headers)

if response.status_code != 200:
    print("Errore nella richiesta Graph API:", response.text)
    exit(1)

events = response.json().get("value", [])

print(f"Eventi Sala Riunioni dalle {start_iso} alle {end_iso}:")

if not events:
    print("- Nessun evento trovato.")
else:
    for event in events:
        start = parser.parse(event["start"]["dateTime"]).astimezone(italy_tz)
        end = parser.parse(event["end"]["dateTime"]).astimezone(italy_tz)
        print(f"- {event['subject']}  da {start} a {end}")
