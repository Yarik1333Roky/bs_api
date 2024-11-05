![bs_api](https://github.com/Yarik1333Roky/bs_api/blob/main/logo.png?raw=true)

![Static Badge](https://img.shields.io/badge/last_update-05.11.2024-highgreen)
![Static Badge](https://img.shields.io/badge/examples-include-highgreen)
![Static Badge](https://img.shields.io/badge/combined_with_API-90%-green)
![Static Badge](https://img.shields.io/badge/version-1.0.0-blue)
![GitHub Issues or Pull Requests](https://img.shields.io/github/issues/Yarik1333Roky/bs_api?logo=github)

## Features
- Simple and well written documentation.
- Latest information about:
  - Rating by *(Top 200)*:
    - Brawlers,
    - Trophies.
  - Players info:
    - Icon image,
    - Username,
    - Battlelog,
    - Brawlers.
  - Brawlers.
  - Club info:
    - Type *(closed, opened, invite only)*,
    - Description,
    - Members.

## Examples

Get player trophies:

```python
from bs_api import ClientBS

TOKEN = os.getenv("TOKEN")
TAG = os.getenv("TAG")

client = ClientBS(TOKEN)

async def main():
    player = await client.get_player(TAG)
    print(player.trophies)

asyncio.run(main())
```

-------------------------

Download player icon image:
```python
from bs_api import ClientBS

TOKEN = os.getenv("TOKEN")
TAG = os.getenv("TAG")

client = ClientBS(TOKEN)

async def main():
    player = await client.get_player(TAG)
    await player.download_icon_image()

asyncio.run(main())
```
Output: 

![](https://github.com/Yarik1333Roky/bs_api/blob/main/output.png?raw=true?scale)

--------------

View top 200 global brawlers and output data using matplotlib:

```python
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
```
*You can find more examples in the examples directory on GitHub.*

## Helping project
You can *help project* by opening [github issues](https://github.com/Yarik1333Roky/bs_api/issues) if needed, helping me improve and modify it.

##### *Thank you for reading this project, have a nice day 🔥🧡*
