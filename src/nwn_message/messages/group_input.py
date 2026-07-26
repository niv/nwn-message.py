from dataclasses import dataclass
from typing import Annotated

from .. import message as m


@dataclass(kw_only=True)
class GroupInputWalkToWayPoint(m.Message):
    MAJOR = 0x26
    MINOR = 0x01
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    position: m.Vec3
    client_path_number: m.Byte
    run_to_point: m.Bool
    client_moving: m.Bool
    move_mode: m.Byte
    clicked_on: m.ObjectId
    group_members: Annotated[list[m.ObjectId], m.SizePrefix.DWORD]


@dataclass(kw_only=True)
class GroupInputAttack(m.Message):
    MAJOR = 0x26
    MINOR = 0x02
    DIRECTION = m.Direction.C2S

    target: m.ObjectId
    group_members: Annotated[list[m.ObjectId], m.SizePrefix.DWORD]
    reserved_tail_bit: Annotated[m.Byte, m.Bits(1)]
