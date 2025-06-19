import asyncio
import os
from pyhon import Hon

async def avvia_clima_custom():
    USER = os.getenv("HON_USER")
    PASSWORD = os.getenv("HON_PASS")
    NICKNAME = "Sala Riunioni"

    async with Hon(USER, PASSWORD) as hon:
        aircon = next((a for a in hon.appliances if a.nick_name == NICKNAME), None)

        if not aircon:
            print("Condizionatore non trovato.")
            return

        start_cmd = aircon.commands.get("startProgram")

        if not start_cmd:
            print("Comando startProgram non disponibile.")
            return

        # Imposta i parametri DENTRO startProgram
        settings = {
            "category": "setParameters",
            "machMode": "1",           # modalità raffreddamento
            "tempSel": 21,             # temperatura desiderata
            "windSpeed": "5",          # massima velocità
            "4SidesWindDirection1": "6",
            "4SidesWindDirection2": "6",
            "4SidesWindDirection3": "6",
            "4SidesWindDirection4": "6"
        }

        for name, setting in start_cmd.settings.items():
            if name in settings:
                setting.value = settings[name]

        print("Avvio il clima con i parametri desiderati...")
        await start_cmd.send()
        print("Climatizzatore avviato.")

if __name__ == "__main__":
    asyncio.run(avvia_clima_custom())
