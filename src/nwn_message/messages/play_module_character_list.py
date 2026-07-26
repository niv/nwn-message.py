from typing import Annotated
from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class PlayModuleCharacterListStart(m.Message):
    MAJOR = 0x31
    MINOR = 0x01
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class PlayModuleCharacterListStop(m.Message):
    MAJOR = 0x31
    MINOR = 0x02
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class PlayModuleCharacterListResponse(m.Message):
    MAJOR = 0x31
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    add: m.Bool
    character_id: m.Dword
    first_name: Annotated[m.LocStr, m.IfEq("add", True)]
    last_name: Annotated[m.LocStr, m.IfEq("add", True)]
    portrait_id: Annotated[m.Word, m.IfEq("add", True)]
    portrait_resref: Annotated[
        m.ResRef, m.IfEq("add", True), m.IfGt("portrait_id", 0xFFFD)
    ]
    classes: Annotated[
        list[tuple[m.Byte, m.Byte]],
        m.IfEq("add", True),
        m.SizePrefix.BYTE,
    ]
