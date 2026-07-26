import asyncio
import configparser
import logging
from functools import lru_cache
from io import StringIO

import nwn.environ
import nwn.resman
import nwn.tlk
import nwn.twoda

from nwn_message import messages
from nwn_message.cdkey import CDKey
from nwn_message.context import Context
from nwn_message.errors import DisconnectedError
from nwn_message.types import LocStr
from nwn_message.websocket import WebsocketClient

logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

logging.getLogger("websockets.client").setLevel(logging.INFO)
logging.getLogger("websockets.server").setLevel(logging.INFO)


class MyContext(Context):
    resman: nwn.resman.ResMan
    dialog_tlk: list[nwn.tlk.Entry]

    def __init__(self):
        self.resman = nwn.resman.create(include_user=False)
        with open(
            nwn.environ.get_install_directory()
            .joinpath("lang/en/data")
            .joinpath("dialog.tlk"),
            "rb",
        ) as f:
            self.dialog_tlk, _lang = nwn.tlk.read(f)

    @lru_cache(maxsize=4096)
    def _get_2da_data(self, twoda: str) -> list:
        tda = self.resman[f"{twoda}.2da"]
        tda2 = nwn.twoda.read(StringIO(tda.decode("utf-8")))
        return list(tda2)

    def twoda_row_count(self, twoda: str) -> int:
        return len(self._get_2da_data(twoda))

    def twoda(self, twoda: str, row: int, column: str) -> str:
        tda = self._get_2da_data(twoda)
        if row >= len(tda):
            raise IndexError(f"Row {row} out of range for 2DA {twoda}")
        if column not in tda[row]:
            raise KeyError(f"Column {column} not found in 2DA {twoda}")
        return tda[row][column]

    def tlk(self, row: int, gender: nwn.types.Gender = nwn.types.Gender.MALE) -> LocStr:
        if row < 0 or row >= len(self.dialog_tlk):
            raise IndexError(f"Row {row} out of range for dialog.tlk")
        return LocStr(
            self.dialog_tlk[row].text,
            str_ref=row,
            gender=gender,
            # [TODO] sounds not supported here
        )


def get_user_cdkey() -> CDKey:
    cfg = configparser.ConfigParser()
    cfg.read(nwn.environ.get_user_directory() / "cdkey.ini")
    return CDKey(cfg.get("NWN1", "YourKey"))


# Pick a vault with at least one character
# Will have to turn off or firewall master auth, or:
# cdkey = CDKey("a-b-c-d-e")
# cdkey = CDKey.generate("ABCDABCD")
cdkey = get_user_cdkey()

context = MyContext()

client = WebsocketClient(
    context_factory=lambda peer: MyContext(),
    player_name="bot",
    cd_key=cdkey,
    host="localhost",
)


@client.on_peer_authenticated.connect
async def on_authenticated(sender, **kw):
    await sender.send(messages.server_status.ServerStatusRequest())
    await sender.send(messages.char_list.CharListRequest())


@client.on(messages.char_list.CharListListResponse).connect
async def on_char_list(sender, data, **kw):
    if not data.characters:
        logger.info("No characters available on the server.")
        return
    char = data.characters[0]
    await sender.send(messages.login.LoginServerSubDirCharacter(resref=char.resref))


@client.on(messages.module.ModuleInfo).connect
async def on_module_info(sender, data, **kw):
    # lies to children
    await sender.send(messages.module.ModuleLoaded())


@client.on(messages.area.AreaClientArea).connect
async def on_area_client_area(sender, data, **kw):
    # lies to children
    await sender.send(messages.area.AreaAreaLoaded())


# You can subscribe to individual GOU bits, you don't need to grab the whole
# packet and walk it.
@client.on(messages.game_obj_update.GameObjUpdateObjListAddCreature).connect
async def on_creature_added(sender, data, **kw):
    # You can breakpoint and inspect, but keep in mind server will time you out.
    # breakpoint()
    ...


async def main():
    try:
        await client.run()
    except DisconnectedError as e:
        logger.exception(e)


if __name__ == "__main__":
    asyncio.run(main())
