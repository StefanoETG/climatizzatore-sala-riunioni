import datetime
import json
import os
import requests
from dateutil import tz, parser
from msal import ConfidentialClientApplication
from check_calendar import get_calendar_events, get_access_token

# Configurazioni
REPLIT_URL = os.getenv("REPLIT_URL")              # per comandi start/stop
REPLIT_URL_STATE = os.getenv("REPLIT_URL_STATE")  # per leggere/scrivere stato JSON
REPLIT_TOKEN = os.getenv("REPLIT_TOKEN")

TIMEZONE = tz.gettz("Europe/Rome")

def load_state():
    """Carica lo stato remoto da Replit."""
    try:
        headers = {"Authorization": f"Bearer {REPLIT_TOKEN}"}
        resp = requests.get(REPLIT_URL_STATE, headers=headers)
        if resp.status_code == 200:
            return resp.json()
        else:
            print(f"Errore caricamento stato remoto: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Eccezione caricamento stato remoto: {e}")
    # fallback a stato di default
    return {"climate_on": False, "last_off_time": None}

def save_state(state):
    """Salva lo stato remoto su Replit."""
    try:
        headers = {
            "Authorization": f"Bearer {REPLIT_TOKEN}",
            "Content-Type": "application/json"
        }
        resp = requests.post(REPLIT_URL_STATE, headers=headers, json=state)
        if resp.status_code == 200:
            print("Stato remoto salvato con successo.")
        else:
            print(f"Errore salvataggio stato remoto: {resp.status_code} {resp.text}")
    except Exception as e:
        print(f"Eccezione salvataggio stato remoto: {e}")

def send_command(action):
    headers = {"Content-Type": "application/json"}
    data = {"action": action, "token": REPLIT_TOKEN}
    resp = requests.post(REPLIT_URL, json=data, headers=headers)
    if resp.status_code == 200:
        print(f"Comando {action} inviato con successo.")
    else:
        print(f"Errore nell'invio comando {action}: {resp.text}")

def main():
    now = datetime.datetime.now(TIMEZONE)
    print(f"Ora corrente: {now}")

    tenant_id = os.environ["AZURE_TENANT_ID"]
    client_id = os.environ["AZURE_CLIENT_ID"]
    client_secret = os.environ["AZURE_CLIENT_SECRET"]
    calendar_id = "salariunioni@etgrisorse.com"

    token = get_access_token(tenant_id, client_id, client_secret)

    start_day = now.replace(hour=8, minute=0, second=0, microsecond=0)
    end_day = now.replace(hour=18, minute=0, second=0, microsecond=0)

    eventi = get_calendar_events(token, calendar_id, start_day, end_day)
    print(f"Eventi oggi: {eventi}")

    state = load_state()
    climate_on = state.get("climate_on", False)
    last_off_time = state.get("last_off_time")
    if last_off_time:
        last_off_time = datetime.datetime.fromisoformat(last_off_time)

    evento_corrente = None
    prossimo_evento = None

    for ev in eventi:
        inizio = parser.isoparse(ev['start']['dateTime']).astimezone(TIMEZONE)
        fine = parser.isoparse(ev['end']['dateTime']).astimezone(TIMEZONE)
        if inizio <= now <= fine:
            evento_corrente = ev
        elif inizio > now and (not prossimo_evento or inizio < parser.isoparse(prossimo_evento['start']['dateTime']).astimezone(TIMEZONE)):
            prossimo_evento = ev

    accendi = False
    spegni = False

    if now.hour == 18 and now.minute < 10:
        if climate_on:
            print("Ora 18:00, spegnimento forzato clima.")
            spegni = True

    if evento_corrente:
        print("Evento in corso, mantieni clima acceso")
        accendi = True
    else:
        if prossimo_evento:
            inizio_prossimo = parser.isoparse(prossimo_evento['start']['dateTime']).astimezone(TIMEZONE)
            delta_inizio = (inizio_prossimo - now).total_seconds() / 60

            if delta_inizio <= 20:
                print("Prossima riunione entro 20 minuti: accendi clima")
                accendi = True
            elif delta_inizio <= 35:
                if climate_on:
                    print("Prossima riunione entro 35 minuti, clima acceso: mantieni acceso")
                    accendi = True
                else:
                    print("Prossima riunione oltre 20 min ma entro 35 min, clima spento: mantieni spento")
                    accendi = False
            else:
                if climate_on:
                    if last_off_time and (now - last_off_time).total_seconds() / 60 >= 20:
                        print("Nessuna riunione entro 35 minuti e 20 min passati da ultimo spegnimento: spegni clima")
                        spegni = True
                    else:
                        print("Nessuna riunione entro 35 minuti ma attendi 20 min dallo spegnimento")
                        accendi = True
                else:
                    print("Clima spento e nessuna riunione prossima: mantieni spento")
                    accendi = False
        else:
            if climate_on:
                if (last_off_time is None) or ((now - last_off_time).total_seconds() / 60 >= 20):
                    print("Fine giornata, spegni clima")
                    spegni = True
                else:
                    print("Fine giornata, attesa spegnimento 20 minuti")
                    accendi = True
            else:
                print("Fine giornata, clima spento")

    if accendi and not climate_on:
        send_command("start")
        state["climate_on"] = True
        state["last_off_time"] = None
        save_state(state)
    elif spegni and climate_on:
        send_command("stop")
        state["climate_on"] = False
        state["last_off_time"] = now.isoformat()
        save_state(state)
    else:
        print("Nessuna azione necessaria.")

if __name__ == "__main__":
    main()
