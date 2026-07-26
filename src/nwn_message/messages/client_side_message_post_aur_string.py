from dataclasses import dataclass
from enum import IntEnum
from typing import Annotated

from .. import message as m


class ScreenAnchor(IntEnum):
    TOP_LEFT = 0
    TOP_RIGHT = 1
    BOTTOM_LEFT = 2
    BOTTOM_RIGHT = 3
    CENTER = 4


@dataclass(kw_only=True)
class ClientSideMessagePostAurString(m.Message):
    MAJOR = 0x12
    MINOR = 0x16

    message: m.String
    id: m.Int
    x: m.Int = 0
    y: m.Int = 0
    anchor: Annotated[ScreenAnchor, m.MessageType.INT] = ScreenAnchor.TOP_LEFT
    rgba1: m.Int = 2147418367
    rgba2: m.Int = 2147418367
    lifetime: m.Float = 10.0
    font: m.ResRef = ""
