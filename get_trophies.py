from bs_api import ClientBS

TOKEN = os.getenv("TOKEN")
TAG = os.getenv("TAG")

client = ClientBS(TOKEN)

async def main():
    player = await client.get_player(TAG)
    print(player.trophies) # Output: 56789

asyncio.run(main())
