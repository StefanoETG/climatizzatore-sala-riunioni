import datetime
import json
import os
import requests
from dateutil import tz
from check_calendar import get_calendar_events  # importa la tua funzione già pronta

# Configurazioni
REPLIT_URL = os.getenv("REPLIT_URL")  # metti il secret in env
REPLIT_TOKEN = os.getenv("REPLIT_TOKEN")

STATE_FILE = "climate_state.json"
TIMEZONE = tz.gettz("Europe/Rome")

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {"climate_on": False, "last_off_time": None}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

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

    # Leggi eventi da calendario dalle 8 di oggi a 18 di oggi
    start_day = now.replace(hour=8, minute=0, second=0, microsecond=0)
    end_day = now.replace(hour=18, minute=0, second=0, microsecond=0)

    eventi = get_calendar_events(start_day.isoformat(), end_day.isoformat())
    print(f"Eventi oggi: {eventi}")

    # Carica stato clima
    state = load_state()
    climate_on = state.get("climate_on", False)
    last_off_time = state.get("last_off_time")
    if last_off_time:
        last_off_time = datetime.datetime.fromisoformat(last_off_time)

    # Trova evento attuale e prossimo evento
    evento_corrente = None
    prossimo_evento = None

    for ev in eventi:
        inizio = datetime.datetime.fromisoformat(ev['start']).astimezone(TIMEZONE)
        fine = datetime.datetime.fromisoformat(ev['end']).astimezone(TIMEZONE)
        if inizio <= now <= fine:
            evento_corrente = ev
        elif inizio > now and (not prossimo_evento or inizio < datetime.datetime.fromisoformat(prossimo_evento['start']).astimezone(TIMEZONE)):
            prossimo_evento = ev

    # Regole di accensione/spegnimento
    accendi = False
    spegni = False

    # Orario spegnimento fisso
    if now.hour == 18 and now.minute < 10:
        # entro i primi 10 minuti delle 18, spegni sempre
        if climate_on:
            print("Ora 18:00, spegnimento forzato clima.")
            spegni = True

    if evento_corrente:
        print("Evento in corso, mantieni clima acceso")
        accendi = True
    else:
        if prossimo_evento:
            inizio_prossimo = datetime.datetime.fromisoformat(prossimo_evento['start']).astimezone(TIMEZONE)
            delta_inizio = (inizio_prossimo - now).total_seconds() / 60  # minuti

            if delta_inizio <= 20:
                print("Prossima riunione entro 20 minuti: accendi clima")
                accendi = True
            elif delta_inizio <= 35:
                # Se clima acceso mantieni acceso
                if climate_on:
                    print("Prossima riunione entro 35 minuti, clima acceso: mantieni acceso")
                    accendi = True
                else:
                    # clima spento e riunione più lontana di 20 min -> mantieni spento
                    print("Prossima riunione oltre 20 min ma entro 35 min, clima spento: mantieni spento")
                    accendi = False
            else:
                # nessuna riunione entro 35 min
                if climate_on:
                    # controlla se sono passati 20 min da fine ultimo evento
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
            # Nessun prossimo evento (fine giornata)
            if climate_on:
                if last_off_time and (now - last_off_time).total_seconds() / 60 >= 20:
                    print("Fine giornata, spegni clima")
                    spegni = True
                else:
                    print("Fine giornata, attesa spegnimento 20 minuti")
                    accendi = True
            else:
                print("Fine giornata, clima spento")

    # Azioni sul clima
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
