from .classes import *
from .errors import ResourceError

class ClientBS(RequestsModel):
    """
    Client to Brawl Stars API.

    Args:
        APIToken (:obj:`str`): Your special token.
    """

    def __init__(self, APIToken: str) -> None:
        super().__init__(APIToken)

    async def get_player(self, tag: str) -> Player:
        """
        Get information about a player by player tag.

        Args:
            tag (:obj:`str`): Target tag.
            EXAMPLE: "#8VJVG4PVC", "#8vjvG4pcv"

        Return:
            `Player`: Player class with all parameters.
        """

        player_data = await self._create_request(f"players/{self._hashtag(tag)}")
        player = Player(player_data, self._token)
        return player

    async def get_player_battlelog(self, tag: str) -> List[Battle]:
        """
        Get player battlelog by his tag. 
        NOTE: It may take up to 30 minutes for a new battle to appear in the battlelog.
        
        Args:
            tag (:obj:`str`): Club tag where need find player.

        Return:
            `List[Battle]`: List of all battles .
        """

        battlelog_data = await self._create_request(f"players/{self._hashtag(tag)}/battlelog")
        return [Battle(battle_data, self._token) for battle_data in battlelog_data["items"]]

    async def get_club(self, tag: str) -> Club:
        """
        Get information about a single clan by club tag.

        Args:
            tag (:obj:`str`): Club target tag.

        Return:
            `Club`: Club class with all parameters.
        """

        club_data = await self._create_request(f"clubs/{self._hashtag(tag)}")
        club = Club(club_data, self._token)

        return club

    async def get_club_members(self, tag: str) -> Club:
        """
        Get list of club members.

        Args:
            tag (:obj:`str`): Club target tag.

        Return:
            `Club`: Club class with all parameters.
        """

        club = await self.get_club(tag)

        return club.members

    async def get_player_by_club(self, clubtag: str, search: str) -> Player:
        """
        Get player by his club tag.

        Args:
            clubtag (:obj:`str`): Club tag where need find player.
            search (:obj:`srt`): Target name or tag.

        Return:
            `Player`: Player class with all parameters.
        """

        targetclub = await self.get_club(clubtag)
        for member in targetclub.members:
            if search.startswith("#"):
                if search in member.tag:
                    return await self.get_player(member.tag)
            else:
                if search in member.name:
                    return await self.get_player(member.tag)

        raise ResourceError("Member was not found.")

    async def get_ranking_clubs(self, countrycode: Literal["global", "contryCode"] = "global") -> List[RankedClub]:
        """
        Get club rankings for a country or global search.

        Args:
            countrycode (:obj:`Literal["global", "contryCode"]`): Country code or global search.
            EXAMPLE: FR, RU, US, global

        Return:
            `List[RankedClub]`: List of classes RankedClub.
        """
        request = await self._create_request(f"rankings/{countrycode.upper()}/clubs")
        returnlist = []
        for info in request["items"]:
            info["ranked_country_code"] = countrycode.upper()
            returnlist.append(RankedClub(info, self._token))

        return returnlist

    async def get_ranking_by_brawlerid(self, brawlerid: int,
                                       countrycode: Literal["global", "contryCode"] = "global"
                                       ) -> List[RankedPlayer]:
        """
        Get brawler rankings for a country or global search.
        brawlerid can be found by using function `get_brawlerid_by_name`

        Args:
            brawlerid (:obj:`int`): Unique id of brawler.
            countrycode (:obj:`Literal["global", "contryCode"]`): Country code or global search.
            EXAMPLE: FR, RU, US, global
        Return:
            `List[RankedPlayer]`: List of classes RankedPlayer.
        """
        request = await self._create_request(f"rankings/{countrycode}/brawlers/{brawlerid}")
        returnlist = []
        for info in request["items"]:
            info["ranked_country_code"] = countrycode.upper()
            returnlist.append(RankedPlayer(info, self._token))

        return returnlist

    async def get_brawlerid_by_name(self, name: str) -> int:
        """
        Get unique brawlerid for use by brawler name.

        Args:
            name (:obj:`str`): Name brawler. 
            EXAMPLE: "LEON", "moe", "ShElLy".

        Return:
            `int`: Unique brawlerid
        """
        request = await self._create_request("brawlers")

        for infobrawler in request["items"]:
            if name.lower() in infobrawler["name"].lower():
                return infobrawler["id"]
            
    async def get_name_by_brawlerid(self, brawlerid: int) -> str:
        """
        Get name brawler by his brawlerid

        Args:
            brawlerid (:obj:`int`): Unique id 

        Return:
            `str`: Name brawler
        """
        request = await self._create_request("brawlers")

        for infobrawler in request["items"]:
            if int(infobrawler["id"]) == brawlerid:
                return infobrawler["name"].capitalize()
            
    async def get_ranking_players(self, countrycode: Literal["global", "contryCode"] = "global") -> List[RankedPlayer]:
        """
        Get player rankings for a country or global search.

        Args:
            countrycode (:obj:`Literal["global", "contryCode"]`): Country code or global search.
            EXAMPLE: FR, RU, US, global

        Return:
            `List[RankedPlayer]`: List of classes RankedPlayer.
        """
        request = await self._create_request(f"rankings/{countrycode}/players")
        return [RankedPlayer(data, self._token) for data in request["items"]]
