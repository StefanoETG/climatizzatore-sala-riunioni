import datetime
from zoneinfo import ZoneInfo
import requests
from msal import ConfidentialClientApplication

# Configurazione variabili ambiente (passate da GitHub secrets)
import os

TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

# Funzione per ottenere token da Azure AD
def get_access_token():
    app = ConfidentialClientApplication(
        CLIENT_ID,
        authority=f"https://login.microsoftonline.com/{TENANT_ID}",
        client_credential=CLIENT_SECRET,
    )
    scopes = ["https://graph.microsoft.com/.default"]
    result = app.acquire_token_silent(scopes, account=None)
    if not result:
        result = app.acquire_token_for_client(scopes=scopes)
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception("Impossibile ottenere token di accesso: " + str(result))

def get_events(access_token, start_time, end_time):
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "startDateTime": start_time.isoformat(timespec='seconds'),
        "endDateTime": end_time.isoformat(timespec='seconds'),
    }
    url = "https://graph.microsoft.com/v1.0/users/salariunioni@etgrisorse.com/calendarView"
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        raise Exception(f"Errore nella richiesta Graph API: {response.text}")
    return response.json().get("value", [])

def main():
    # Usa timezone Europa/Roma
    tz = ZoneInfo("Europe/Rome")

    now = datetime.datetime.now(tz)
    start_time = now
    end_time = now + datetime.timedelta(hours=2)

    print(f"Eventi Sala Riunioni dalle {start_time} alle {end_time}:")

    token = get_access_token()
    events = get_events(token, start_time, end_time)

    if not events:
        print("Nessun evento trovato.")
    else:
        for ev in events:
            subject = ev.get("subject", "Senza titolo")
            start = ev["start"]["dateTime"]
            end = ev["end"]["dateTime"]
            print(f"- {subject}  da {start} a {end}")

if __name__ == "__main__":
    main()
