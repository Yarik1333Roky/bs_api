from aiohttp import ClientSession
from aiohttp import TCPConnector
from typing import List, Literal, Union
from io import BytesIO
from datetime import datetime
import re

from .errors import *

class RequestsModel:
    """
    Basic request model for accessing requests to Brawl Stars API.

    Args:
        APIToken (:obj:`str`): Special token for requests.
    """

    __basic_url = "https://api.brawlstars.com/v1/"

    def __init__(self, APIToken) -> None:
        self._token = APIToken

    def _generate_url(self, add):
        return self.__basic_url + str(add)

    def _hashtag(self, old_str: str):
        if old_str.startswith("#"):
            return old_str.replace("#", "%23")
        else:
            return "%23" + old_str

    async def _create_request(self, url, return_content=False):
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            response = await session.get(
                self._generate_url(url) if not return_content else url,
                headers={"Authorization": f"Bearer {self._token}"},
            )
            if response.status == 200:
                if return_content:
                    return await response.content.read()
                else:
                    return await response.json()
            elif response.status == 400:
                raise IncorrectError()
            elif response.status == 403:
                raise AccessError()
            elif response.status == 404:
                raise ResourceError()
            elif response.status == 429:
                raise RequestsLimitError()
            elif response.status == 503:
                raise ServiceError()
            else:
                raise UnknownError(
                    f"Unknown error happened when handling the request with {response.status} status."
                )


class BasicPlayer(RequestsModel):
    """
    Basic player class for finding player.
    """
    def __init__(self, APIToken) -> None:
        super().__init__(APIToken)

    async def get_player(self):
        """
        Get real `Player` class of player.

        Return:
            `Player`: Real `Player` class with all his parameters.
        """
        player_data = await self._create_request(f"players/{self._hashtag(self.tag)}")
        player = Player(player_data, self._token)
        return player


class Club(RequestsModel):
    """
    basic club class with all parameters.

    Args:
        tag (:obj:`str`): Club tag.
        name (:obj:`str`): Club name.
        description (:obj:`str`): Description of club.
        type (:obj:`Literal["open", "closed", "inviteOnly"]`): type club.
        badge_id (:obj:`int`): ID badge of this club.
        required_trophies (:obj:`int`): Required trophies for joining in club.
        trophies (:obj:`int`): Total trophies in club.
        members (:obj:`List[Member]`): List of all members in club.
    """
    def __init__(self, my_data, APIToken) -> None:
        super().__init__(APIToken)
        self.tag: str = ""
        self.name: str = ""
        self.description: str = ""
        self.type: Literal["open", "closed", "inviteOnly"] = ""
        self.badge_id: int = 0
        self.required_trophies: int = 0
        self.trophies: int = 0
        self.members: List[Member] = []

        for value in my_data:
            setattr(self, re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower(), my_data[value])

        new_members = []
        for member in self.members:
            newMember = Member(member, self._token)
            new_members.append(newMember)
        self.members = new_members

    async def get_player_by_search(self, search: str):
        """
        Get player by his name or tag.

        Args:
            search (:obj:`srt`): Target name or tag.

        Return:
            `Player`: Player class with all parameters.
        """

        for member in self.members:
            if search.startswith("#"):
                if search in member.tag:
                    return await member.get_player()
            else:
                if search in member.name:
                    return await member.get_player()

        raise ResourceError("Member was not found.")

    def __repr__(self) -> str:
        return f"<Club object name='{self.name}' tag='{self.tag}'>"


class Brawler:
    """
    Brawler class of specific player with all brawler statistic.

    Args:
        id (:obj:`int`): Unique ID of brawler.
        name (:obj:`srt`): Name brawler.
        power (:obj:`int`): Power of brawler.
        rank (:obj:`srt`): Rank of brawler.
        trophies (:obj:`int`): Trophies of brawler.
        highest_trophies (:obj:`int`): Highest trophies of brawler.
        gears (:obj:`list`): All gears of brawler.
        star_powers (:obj:`list`): All star powers of brawler.
        gadgets (:obj:`list`): All gadgets of brawler.
    """
    def __init__(self, data) -> None:
        self.id: int = 0
        self.name: str = ""
        self.power: int = ""
        self.rank: int = 0
        self.trophies: int = 0
        self.highest_trophies: int = 0
        self.gears: list = []
        self.star_powers: list = []
        self.gadgets: list = []

        for value in data:
            setattr(self, re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower(), data[value])

    def __repr__(self) -> str:
        return f"<Brawler object name='{self.name}' trophies='{self.trophies}'>"


class Battler(BasicPlayer):
    """
    Battler class of battle for specific player.

    Args:
        tag (:obj:`str`): Tag player.
        name (:obj:`srt`): Name player.
        brawler_name (:obj:`str`): Brawler name.
        brawler_id (:obj:`int`): Unique id of brawler (brawlerid).
        brawler_power (:obj:`int`): Bralwer power.
        brawler_trophies (:obj:`int`): Current brawler trophies.
    """
    def __init__(self, my_data, APIToken) -> None:
        super().__init__(APIToken)

        self.tag: str = ""
        self.name: str = ""
        self.brawler_name: str = ""
        self.brawler_id: int = 0
        self.brawler_power: int = 0
        self.brawler_trophies: int = 0

        for value in my_data:
            if str(value) == "brawler":
                for brawler_value in my_data[value]:
                    setattr(
                        self, "brawler_" + brawler_value, my_data[value][brawler_value]
                    )
            else:
                setattr(self, value, my_data[value])

    async def get_brawler(self) -> Brawler:
        """
        Get `Brawler` class with all his parameters.

        Return:
            `Brawler`: original brawler class.
        """

        player = await self.get_player()
        for brawler in player.brawlers:
            if brawler.id == self.brawler_id:
                return brawler

    def __repr__(self) -> str:
        return f"<Battler object name='{self.name}' brawler_name='{self.brawler_name}'>"


class Battle(RequestsModel):
    """
    Battle class from unique battlelog.

    Args:
        battle_time (:obj:`datetime.datetime`): Time of battle (UTC+00).
        id (:obj:`int`): Unique id of map.
        mode (:obj:`str`): Mode of battle.
        map (:obj:`str`): Map name.
        type (:obj:`str`): Type of battle.
        result (:obj:`Literal["defeat", "victory", "draw"]`): Result of match.
        duration (:obj:`int`): Duration in sec.
        trophy_change (:obj:`int`): How much player get trophies for this battle.
        rank (:obj:`int`): Rank of battler which player was playing on.
    """
    def __init__(self, my_data, APIToken) -> None:
        super().__init__(APIToken)

        self.battle_time: datetime
        self.id: int = 0
        self.mode: str = ""
        self.map: str = ""
        self.type: str = ""
        self.result: Literal["defeat", "victory", "draw"] = ""
        self.duration: int = 0
        self.trophy_change: int = 0
        self.rank: int = 0

        for value in my_data:
            if value in ["event", "battle"]:
                for attr in my_data[value]:
                    setattr(self, re.sub(r'(?<!^)(?=[A-Z])', '_', attr).lower(), my_data[value][attr])
            elif value == "battleTime":
                time = my_data[value]
                real_time = (
                    time[0:4]
                    + "-"
                    + time[4:6]
                    + "-"
                    + time[6:11]
                    + ":"
                    + time[11:13]
                    + ":"
                    + time[13:15]
                )
                self.battle_time = datetime.strptime(real_time, "%Y-%m-%dT%H:%M:%S")

    async def get_star_player(self):
        """
        Get star player of this battle

        Return:
            'Player': star player.
        """
        if self.__dict__.get("starPlayer"):
            player_data = await self._create_request(
                f"players/{self._hashtag(self.__dict__['starPlayer']['tag'])}"
            )
            star_player = Player(player_data, self._token)
            return star_player
        else:
            return None

    def get_battlers(self) -> List[Battler]:
        """
        Get list of `Battler`'s from current battle.

        Return:
            `List[Battler]`: List of all `Battler`'s in this battle.
        """
        output = []
        if self.__dict__.get("players"):
            for player in self.__dict__.get("players"):
                output.append(Battler(player, self._token))
        elif self.__dict__.get("teams"):
            for team in self.__dict__.get("teams"):
                output_team = []
                for player in team:
                    output_team.append(Battler(player, self._token))
                output.append(output_team)

        return output

    def __repr__(self) -> str:
        return f"<Battle object mode='{self.mode}' result='{self.result}'>"


class Player(RequestsModel):
    """
    Player class of specific client in brawl stars.

    Args:
        tag (:obj:`str`): Tag player.
        name (:obj:`srt`): Name player.
        is_qualified_from_championship_challenge (:obj:`bool`): check if player is qualified from championship challenge.
        trophies (:obj:`int`): Trophies of player.
        exp_level (:obj:`int`): Experience level.
        exp_points (:obj:`int`): Experience points.
        highest_trophies (:obj:`int`): Highest possible trophies of player.
        victories3vs3 (:obj:`int`): Number of victories in 3vs3 battles.
        solo_victories (:obj:`int`): Number of victories in solo battles.
        duo_victories (:obj:`int`): Number of victories in duo battles.
        best_robo_rumble_time (:obj:`int`): Best robo rumble event time.
        best_time_as_big_brawler (:obj:`int`): Best time as big brawler event.
        name_color (:obj:`str`): Specific color of name.
        brawlers (:obj:`List[Brawler]`): List of all brawlers on account player.
    """
    
    __basic_icon_url = "https://cdn.brawlify.com/profile-icons/regular/"

    def __init__(self, my_data, APIToken) -> None:
        super().__init__(APIToken)

        self.tag: str = ""
        self.name: str = ""
        self.is_qualified_from_championship_challenge: bool = False
        self.trophies: int = 0
        self.exp_level: int = 0
        self.exp_points: int = 0
        self.highest_trophies: int = 0
        self.solo_victories: int = 0
        self.duo_victories: int = 0
        self.best_robo_rumble_time: int = 0
        self.best_time_as_big_brawler: int = 0
        self.name_color: str = 0
        self.brawlers: List[Brawler] = []

        self._club: Club = None
        self._icon: dict = {"id": 0}

        for value in my_data:
            if value in ["club", "icon"]:
                setattr(self, f"_{value}", my_data[value])
            else:
                setattr(self, re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower(), my_data[value])

        new_brawlers = []
        for brawler in self.brawlers:
            newBrawler = Brawler(brawler)
            new_brawlers.append(newBrawler)
        self.brawlers = new_brawlers

    @property
    def victories3vs3(self):
        return self.__dict__["3vs3Victories"]

    def _generate_icon_url(self, add):
        return self.__basic_icon_url + str(add) + ".png"

    async def get_bytes_icon_image(self) -> BytesIO:
        """
        Get `BytesIO` of request to url icon image.

        Return:
            `BytesIO`: buffer of icon image.
        """
        content = await self._create_request(
            self._generate_icon_url(self._icon["id"]), return_content=True
        )
        return content

    async def download_icon_image(self, path: str = "output") -> None:
        """
        Download player icon image to specific path.

        Args:
            path (:obj:`str`): Path to download the image.
        """
        icon_bytes = await self.get_bytes_icon_image()

        with open(path + ".png", "wb") as file:
            file.write(icon_bytes)
            file.close()

    async def get_club(self) -> Union[Club]:
        """
        Get club where the player is joined.

        Return:
            `Club`: player club.
        """
        if len(self._club) > 0:
            club_data = await self._create_request(
                f"clubs/{self._hashtag(self._club['tag'])}"
            )
            club = Club(club_data, self._token)
            return club
        else:
            return None

    async def get_battlelog(self) -> List[Battle]:
        """
        Get battlelog of the player's last 25 battles.

        Return:
            `List[Battle]`: battlelog.
        """
        battlelog_data = await self._create_request(
            f"players/{self._hashtag(self.tag)}/battlelog"
        )
        battlelog = []
        for battle_data in battlelog_data["items"]:
            battlelog.append(Battle(battle_data, self._token))
        return battlelog

    def __repr__(self):
        return f"<Player object name='{self.name}' tag='{self.tag}'>"


class Member(BasicPlayer):
    """
    Club member class.

    Args:
        tag (:obj:`str`): Tag member.
        name (:obj:`srt`): Name member.
        name_color (:obj:`str`): Specific color of name.
        role (:obj:`Literal["member", "senior", "vicePresident", "president"]`): Role in club.
        trophies (:obj:`int`): Trophies of member.
    """
    def __init__(self, my_data, APIToken) -> None:
        super().__init__(APIToken)

        self.tag: str = ""
        self.name: str = ""
        self.name_color: str = ""
        self.role: Literal["member", "senior", "vicePresident", "president"] = "member"
        self.trophies: int = 0

        for value in my_data:
            setattr(self, re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower(), my_data[value])

    def __repr__(self):
        return f"<Member object name='{self.name}' role='{self.role}'>"


class RankedClub(RequestsModel):
    """
    Ranked club from ranking functional.

    Args:
        tag (:obj:`str`): Tag club.
        name (:obj:`srt`): Name club.
        badge_id (:obj:`int`): ID badge of this club.
        trophies (:obj:`int`): Total trophies in club.
        rank (:obj:`int`): Rank of club in ranking function.
        member_count (:obj:`int`): Number of members in this club.
        ranked_country_code (:obj:`str`): Country code of this ranked club in ranking function.
    """
    def __init__(self, my_data, APIToken) -> None:
        super().__init__(APIToken)
        self.tag: str = ""
        self.name: str = ""
        self.badge_id: int = 0
        self.trophies: int = 0
        self.rank: int = 0
        self.member_count: int = 0
        self.ranked_country_code: str = ""

        for value in my_data:
            setattr(self, re.sub(r'(?<!^)(?=[A-Z])', '_', value).lower(), my_data[value])

    def __repr__(self) -> str:
        return f"<RankedClub object name='{self.name}' rank='{self.tag}'>"

    async def get_club(self) -> Club:
        """
        Get real `Club` class.

        Return:
            `Club`: `Club` class
        """
        club_data = await self._create_request(f"clubs/{self._hashtag(self.tag)}")
        club = Club(club_data, self._token)
        return club


class RankedPlayer(BasicPlayer):
    """
    Ranked player from ranking functional.

    Args:
        tag (:obj:`str`): Tag player.
        name (:obj:`srt`): Name player.
        trophies (:obj:`int`): Total trophies in club.
        rank (:obj:`int`): Rank of player in ranking function.
        club_name (:obj:`str`): Name of club when player is joined.
        ranked_country_code (:obj:`str`): Country code of this ranked club in ranking function.
    """
    def __init__(self, my_data, APIToken) -> None:
        super().__init__(APIToken)

        self.tag: str = ""
        self.name: str = ""
        self.trophies: int = 0
        self.rank: int = 0
        self.club_name: str = ""
        self.ranked_country_code: str = ""

        for value in my_data:
            if value == "club":
                setattr(self, "club_name", my_data[value]["name"])
            elif value != "icon":
                setattr(self, value, my_data[value]["id"])

    def __repr__(self) -> str:
        return f"<RankedPlayer object name='{self.name}' rank='{self.rank}'>"
