from typing import Annotated
from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class SaveLoadStatus(m.Message):
    MAJOR = 0x2D
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    stall_event_type: m.Byte
    status: Annotated[m.Dword, m.Bits(4)]
