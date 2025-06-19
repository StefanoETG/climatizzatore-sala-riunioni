import os
import datetime
import pytz
from msal import ConfidentialClientApplication
import requests
from dateutil import parser

# Configura il fuso orario locale (Roma)
tz = pytz.timezone("Europe/Rome")

def get_access_token(tenant_id, client_id, client_secret):
    app = ConfidentialClientApplication(
        client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        client_credential=client_secret,
    )
    result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception(f"Errore nell'acquisizione token: {result.get('error_description')}")

def get_calendar_events(access_token, calendar_id, start_datetime, end_datetime):
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "startDateTime": start_datetime.isoformat(),
        "endDateTime": end_datetime.isoformat(),
        "$orderby": "start/dateTime",
    }
    url = f"https://graph.microsoft.com/v1.0/users/{calendar_id}/calendarview"
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Errore nella richiesta Graph API: {response.text}")
    return response.json().get("value", [])

def main():
    tenant_id = os.environ["AZURE_TENANT_ID"]
    client_id = os.environ["AZURE_CLIENT_ID"]
    client_secret = os.environ["AZURE_CLIENT_SECRET"]
    calendar_id = "salariunioni@etgrisorse.com"

    # Ora locale e ora 2 ore dopo per l'intervallo di ricerca
    now = datetime.datetime.now(tz)
    later = now + datetime.timedelta(hours=2)

    access_token = get_access_token(tenant_id, client_id, client_secret)

    events = get_calendar_events(access_token, calendar_id, now, later)

    print(f"Eventi Sala Riunioni dalle {now} alle {later}:")

    if not events:
        print("Nessun evento trovato.")
    else:
        for ev in events:
            subject = ev.get("subject", "Senza titolo")
            start = parser.isoparse(ev["start"]["dateTime"]).astimezone(tz)
            end = parser.isoparse(ev["end"]["dateTime"]).astimezone(tz)
            print(f"- {subject}  da {start} a {end}")

if __name__ == "__main__":
    main()
