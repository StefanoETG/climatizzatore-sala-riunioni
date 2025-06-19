import msal
import requests
import datetime
import os

# Prendi i valori dai secrets GitHub impostati come variabili d’ambiente
TENANT_ID = os.getenv("AZURE_TENANT_ID")
CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")
RESOURCE_EMAIL = "salariunioni@etgrisorse.com"

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPE = ["https://graph.microsoft.com/.default"]
GRAPH_ENDPOINT = "https://graph.microsoft.com/v1.0"

def get_access_token():
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=CLIENT_SECRET,
    )
    result = app.acquire_token_for_client(scopes=SCOPE)
    if "access_token" in result:
        return result["access_token"]
    else:
        raise Exception("Impossibile ottenere token: " + str(result))

def get_calendar_events(token, start_time, end_time):
    headers = {"Authorization": "Bearer " + token}
    url = f"{GRAPH_ENDPOINT}/users/{RESOURCE_EMAIL}/calendarView"
    params = {
        "startDateTime": start_time.isoformat(),
        "endDateTime": end_time.isoformat(),
        "$orderby": "start/dateTime",
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json().get("value", [])

def main():
    now = datetime.datetime.utcnow()
    start = now
    end = now + datetime.timedelta(hours=2)

    token = get_access_token()
    events = get_calendar_events(token, start, end)

    print(f"Eventi Sala Riunioni dalle {start} alle {end}:")
    for ev in events:
        print(f"- {ev['subject']} da {ev['start']['dateTime']} a {ev['end']['dateTime']}")

if __name__ == "__main__":
    main()
