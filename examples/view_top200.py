import matplotlib.pyplot as plt
from bs_api import ClientBS

TOKEN = os.getenv("TOKEN")
TAG = os.getenv("TAG")

client = ClientBS(TOKEN)

async def main():
    plt.figure(figsize=(7, 5))

    need = {"bea": "pink", "sprout": "gray", "leon": "green", "gene": "purple"}
    for brawler in need:
        brawlerId = await client.get_brawlerid_by_name(brawler)
        rankingBrawler = await client.get_ranking_by_brawlerid(brawlerId)
        plt.plot([data.trophies for data in rankingBrawler], marker = 'o', linestyle = '-', color = need[brawler])

    plt.ylabel('Trophies')
    plt.show()

asyncio.run(main())
