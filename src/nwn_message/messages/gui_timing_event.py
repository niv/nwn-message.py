from typing import Annotated
from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class GuiTimingEventInfo(m.Message):
    MAJOR = 0x30
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    starting: m.Bool
    duration: Annotated[m.Dword, m.IfEq("starting", True)]
    event_type: Annotated[m.Byte, m.IfEq("starting", True)]
