from dataclasses import dataclass
from typing import Annotated

from .. import message as m

INVALID_OBJECT_ID = 0x7F000000


@dataclass(kw_only=True)
class GoldTransferGold(m.Message):
    MAJOR = 0x08
    MINOR = 0x01
    DIRECTION = m.Direction.C2S

    object_id: m.ObjectId
    amount: m.Int
    barter: m.Bool
    destination: Annotated[m.Vec3, m.IfEq("object_id", INVALID_OBJECT_ID)]
    x_pos: Annotated[m.Byte, m.IfEq("barter", True)]
    y_pos: Annotated[m.Byte, m.IfEq("barter", True)]
