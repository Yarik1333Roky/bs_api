from bs_api import ClientBS
from datetime import datetime

TOKEN = os.getenv("TOKEN")
TAG = os.getenv("TAG")

client = ClientBS(TOKEN)

async def main():
    player = await client.get_player(TAG)
    
    showdown = player.duoVictories + player.soloVictories
    if showdown >= player.victories3vs3:
        print(f"More wins in showdown than in 3vs3 on {100-player.victories3vs3/showdown*100}%")
    else:
        print(f"More wins in 3vs3 than in showdown on {100-showdown/player.victories3vs3*100}%")

asyncio.run(main())
