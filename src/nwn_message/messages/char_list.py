from typing import Annotated
from dataclasses import dataclass, field
from enum import IntEnum

from .. import message as m


@dataclass(kw_only=True)
class CharListRequest(m.Message):
    MAJOR = 0x11
    MINOR = 0x01
    DIRECTION = m.Direction.C2S


class CharacterType(IntEnum):
    SERVER = 0x02
    SERVER_SAVEGAME = 0xE
    SERVER_SUBDIR = 0x11


@dataclass(kw_only=True)
class CharListListResponse(m.Message):
    MAJOR = 0x11
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    @dataclass(kw_only=True)
    class Character:
        first_name: m.LocStr
        last_name: m.LocStr
        resref: m.ResRef
        type: Annotated[CharacterType, m.MessageType.BYTE]
        portrait_id: m.Word
        portrait_resref: m.ResRef
        classes: Annotated[list[tuple[m.Int, m.Byte]], m.SizePrefix.BYTE]

    characters: Annotated[list[Character], m.SizePrefix.WORD]


@dataclass(kw_only=True)
class CharListRequestUpdateChar(m.Message):
    MAJOR = 0x11
    MINOR = 0x03
    DIRECTION = m.Direction.C2S

    char_type: m.Byte
    resref: m.ResRef


@dataclass(kw_only=True)
class CharListUpdateCharResponse(m.Message):
    MAJOR = 0x11
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    char_type: m.Byte
    resref: m.ResRef
    data: m.Void = field(repr=False)
