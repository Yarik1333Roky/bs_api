from aiohttp import ClientSession
from aiohttp import TCPConnector
from typing import List, Literal
from io import BytesIO
from datetime import datetime

from .errors import *


class RequestsModel:
    __basic_url = "https://api.brawlstars.com/v1/"

    def __init__(self, APItoken) -> None:
        self._token = APItoken

    def _generate_url(self, add):
        return self.__basic_url + str(add)

    def _hashtag(self, old_str: str):
        return old_str.replace("#", "%23")

    async def _create_request(self, url, return_content=False):
        async with ClientSession(connector=TCPConnector(ssl=False)) as session:
            response = await session.get(
                self._generate_url(url),
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
    def __init__(self, APIToken) -> None:
        super().__init__(APIToken)

    async def get_player(self):
        player_data = await self._create_request(f"players/{self._hashtag(self.tag)}")
        player = Player(player_data, self._token)
        return player


class Club(RequestsModel):
    def __init__(self, my_data, APIToken) -> None:
        super().__init__(APIToken)
        self.tag: str = ""
        self.name: str = ""
        self.description: str = ""
        self.type: Literal["open", "closed", "inviteOnly"] = ""
        self.badgeId: int = 0
        self.requiredTrophies: int = 0
        self.trophies: int = 0
        self.members: List[Member] = []

        for value in my_data:
            setattr(self, value, my_data[value])

        new_members = []
        for member in self.members:
            newMember = Member(member, self._token)
            new_members.append(newMember)
        self.members = new_members

    def __repr__(self) -> str:
        return f"<Club object name='{self.name}' tag='{self.tag}'>"


class Brawler:
    def __init__(self, data) -> None:
        self.id: int = 0
        self.name: str = ""
        self.power: str = ""
        self.rank: int = 0
        self.trophies: int = 0
        self.highestTrophies: int = 0
        self.gears: list = []
        self.starPowers: list = []
        self.gadgets: list = []

        for value in data:
            setattr(self, value, data[value])

    def __repr__(self) -> str:
        return f"<Brawler object name='{self.name}' trophies='{self.trophies}'>"


class Battler(BasicPlayer):
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

    def __repr__(self) -> str:
        return f"<Battler object name='{self.name}' brawler_name='{self.brawler_name}'>"


class Battle(RequestsModel):
    def __init__(self, my_data, APIToken) -> None:
        super().__init__(APIToken)

        self.battleTime: datetime
        self.id: int = 0
        self.mode: str = ""
        self.map: str = ""
        self.type: str = ""
        self.result: Literal["defeat", "victory", "draw"] = ""
        self.duration: int = 0
        self.trophyChange: int = 0
        self.rank: int = None

        for value in my_data:
            if value == "event":
                for types in my_data[value]:
                    setattr(self, f"{types}", my_data[value][types])
            elif value == "battle":
                for attr in my_data[value]:
                    setattr(self, f"{attr}", my_data[value][attr])
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
                self.battleTime = datetime.strptime(real_time, "%Y-%m-%dT%H:%M:%S")

    async def get_star_player(self):
        if self.__dict__.get("starPlayer"):
            player_data = await self._create_request(
                f"players/{self._hashtag(self.__dict__['starPlayer']['tag'])}"
            )
            star_player = Player(player_data, self._token)
            return star_player
        else:
            return None

    def get_battlers(self) -> List[Battler]:
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
    __basic_icon_url = "https://cdn.brawlify.com/profile-icons/regular/"

    def __init__(self, my_data, APIToken) -> None:
        super().__init__(APIToken)

        self.isQualifiedFromChampionshipChallenge: bool = False
        self.tag: str = ""
        self.name: str = ""
        self.trophies: int = 0
        self.expLevel: int = 0
        self.expPoints: int = 0
        self.highestTrophies: int = 0
        self.soloVictories: int = 0
        self.duoVictories: int = 0
        self.bestRoboRumbleTime: int = 0
        self.bestTimeAsBigBrawler: int = 0
        self.nameColor: str = 0
        self._club: Club = None
        self._icon: dict = {"id": 0}
        self.brawlers: List[Brawler] = []

        for value in my_data:
            if value in ["club", "icon"]:
                setattr(self, f"_{value}", my_data[value])
            else:
                setattr(self, value, my_data[value])

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
        content = await self._create_request(
            self._generate_icon_url(self._icon["id"]), return_content=True
        )
        return content

    async def download_icon_image(self, path: str = "output") -> None:
        icon_bytes = await self._create_request(
            self._generate_icon_url(self._icon["id"]), return_content=True
        )

        with open(path + ".png", "wb") as file:
            file.write(icon_bytes)
            file.close()

    async def get_club(self) -> Club:
        if len(self._club) > 0:
            club_data = await self._create_request(
                f"clubs/{self._hashtag(self._club['tag'])}"
            )
            club = Club(club_data, self._token)
            return club
        else:
            return None

    async def get_battlelog(self) -> List[Battle]:
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
    def __init__(self, my_data, APIToken) -> None:
        super().__init__(APIToken)

        self.tag: str = ""
        self.name: str = ""
        self.nameColor: str = ""
        self.role: Literal["member", "senior", "vicePresident", "president"] = "member"
        self.trophies: int = 0

        for value in my_data:
            setattr(self, value, my_data[value])

    def __repr__(self):
        return f"<Member object name='{self.name}' role='{self.role}'>"


class RankedClub(RequestsModel):
    def __init__(self, my_data, APIToken) -> None:
        super().__init__(APIToken)
        self.tag: str = ""
        self.name: str = ""
        self.badgeId: int = 0
        self.trophies: int = 0
        self.rank: int = 0
        self.memberCount: int = 0
        self.rank_from: str = ""

        for value in my_data:
            setattr(self, value, my_data[value])

    def __repr__(self) -> str:
        return f"<RankedClub object name='{self.name}' rank='{self.tag}'>"

    async def get_club(self) -> Club:
        club_data = await self._create_request(f"clubs/{self._hashtag(self.tag)}")
        club = Club(club_data, self._token)
        return club


class RankedPlayer(BasicPlayer):
    def __init__(self, my_data, APIToken) -> None:
        super().__init__(APIToken)

        self.tag: str = ""
        self.name: str = ""
        self.icon: int = 0
        self.trophies: int = 0
        self.rank: int = 0
        self.club_name: str = ""

        for value in my_data:
            if value == "club":
                setattr(self, "club_name", my_data[value]["name"])
            elif value == "icon":
                setattr(self, value, my_data[value]["id"])
            else:
                setattr(self, value, my_data[value])

    def __repr__(self) -> str:
        return f"<RankedPlayer object name='{self.name}' rank='{self.rank}'>"
