import asyncio
import os
from pyhon import Hon

async def spegni_sala_riunioni():
    USER = os.getenv("HON_USER")
    PASSWORD = os.getenv("HON_PASS")
    NICKNAME = "Sala Riunioni"

    async with Hon(USER, PASSWORD) as hon:
        aircon = None
        for appliance in hon.appliances:
            if appliance.nick_name == NICKNAME:
                aircon = appliance
                break

        if aircon is None:
            print("Condizionatore non trovato con quel nickname.")
            return

        # Comando di stop
        stop_cmd = aircon.commands.get("stopProgram")
        if not stop_cmd:
            print("Comando stopProgram non disponibile.")
            return

        print("Invio comando stopProgram...")
        await stop_cmd.send()
        print("Condizionatore spento.")

if __name__ == "__main__":
    asyncio.run(spegni_sala_riunioni())
