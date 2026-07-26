from dataclasses import dataclass
from typing import Annotated

from nwn.types import Platform

from .. import message as m


@dataclass(kw_only=True)
class Player:
    player_id: m.Dword
    object_id: m.ObjectId
    is_dm: m.Bool
    player_name: m.String
    is_primary_pc: m.Bool
    platform_id: Annotated[Platform, m.MessageType.BYTE]
    psid: m.String = ""

    @dataclass(kw_only=True)
    class PrimaryPC:
        object_id: m.ObjectId
        first_name: m.LocStr
        last_name: m.LocStr
        portrait_id: m.Word
        portrait_resref: Annotated[m.ResRef, m.IfGt("portrait_id", 0xFFFD)]

    primary_pc: Annotated[PrimaryPC, m.IfEq("is_primary_pc", True)]


@dataclass(kw_only=True)
class PlayerListFull(m.Message):
    MAJOR = 0x0A
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    display_dm_msg: m.Bool = True
    players: Annotated[list[Player], m.SizePrefix.BYTE]


@dataclass(kw_only=True)
class PlayerListAdd(m.Message):
    MAJOR = 0x0A
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    display_dm_msg: m.Bool = True
    player: Player


@dataclass(kw_only=True)
class PlayerListDelete(m.Message):
    MAJOR = 0x0A
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    display_dm_msg: m.Bool
    player_id: m.Dword


@dataclass(kw_only=True)
class PlayerListReauthorizeCDKey(m.Message):
    MAJOR = 0x0A
    MINOR = 0x04

    challenge: m.String
    key: m.String
