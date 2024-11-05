from bs_api import ClientBS
from datetime import datetime

TOKEN = os.getenv("TOKEN")
TAG = os.getenv("TAG")

client = ClientBS(TOKEN)

async def main():
    player = await client.get_player(TAG)
    battlelog = await player.get_battlelog()
    deltatime = datetime.now() - battlelog[0].battleTime
    
    print(f"{player.name} last battle was {deltatime} ago")

asyncio.run(main())
