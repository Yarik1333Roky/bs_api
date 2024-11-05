from bs_api import ClientBS

TOKEN = os.getenv("TOKEN")
TAG = os.getenv("TAG")

client = ClientBS(TOKEN)

async def main():
    player = await client.get_player(TAG)
    await player.download_icon_image()

asyncio.run(main())
