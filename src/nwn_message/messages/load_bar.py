from typing import Annotated
from enum import IntEnum
from dataclasses import dataclass

from .. import message as m


class StallEvent(IntEnum):
    NONE = 0
    LOAD_GAME = 1
    SAVE_GAME = 2
    LOAD_SAVE = 3


@dataclass(kw_only=True)
class LoadBarStart(m.Message):
    MAJOR = 0x2C
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    stall_event: Annotated[StallEvent, m.MessageType.DWORD]


@dataclass(kw_only=True)
class LoadBarUpdate(m.Message):
    MAJOR = 0x2C
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    completed_work: m.Dword
    total_work: m.Dword


@dataclass(kw_only=True)
class LoadBarEnd(m.Message):
    MAJOR = 0x2C
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    stall_event: Annotated[StallEvent, m.MessageType.DWORD]
    error: Annotated[m.Dword, m.Bits(4)]
