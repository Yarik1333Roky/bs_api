from bs_api import ClientBS

TOKEN = os.getenv("TOKEN")
CLUB_TAG = os.getenv("CLUB_TAG")

client = ClientBS(TOKEN)

async def main():
    target = await client.get_player_by_club(CLUB_TAG, "Roky")
    print(target) # Output: <Player object name='[БЛЕТ] Roky' tag='#8VLVG8PCJ'>
    print(target.name, target.tag) # Output: [БЛЕТ] Roky #8VLVG8PCJ

asyncio.run(main())
