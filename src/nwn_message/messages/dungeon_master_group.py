from dataclasses import dataclass
from typing import Annotated

from .. import message as m


@dataclass(kw_only=True)
class DungeonMasterGroupHeal(m.Message):
    MAJOR = 0x27
    MINOR = 0x20
    DIRECTION = m.Direction.C2S

    targets: Annotated[list[m.ObjectId], m.SizePrefix.DWORD]


@dataclass(kw_only=True)
class DungeonMasterGroupKill(m.Message):
    MAJOR = 0x27
    MINOR = 0x21
    DIRECTION = m.Direction.C2S

    targets: Annotated[list[m.ObjectId], m.SizePrefix.DWORD]


@dataclass(kw_only=True)
class DungeonMasterGroupInvulnerable(m.Message):
    MAJOR = 0x27
    MINOR = 0x24
    DIRECTION = m.Direction.C2S

    targets: Annotated[list[m.ObjectId], m.SizePrefix.DWORD]


@dataclass(kw_only=True)
class DungeonMasterGroupRest(m.Message):
    MAJOR = 0x27
    MINOR = 0x25
    DIRECTION = m.Direction.C2S

    targets: Annotated[list[m.ObjectId], m.SizePrefix.DWORD]


@dataclass(kw_only=True)
class DungeonMasterGroupLimbo(m.Message):
    MAJOR = 0x27
    MINOR = 0x26
    DIRECTION = m.Direction.C2S

    targets: Annotated[list[m.ObjectId], m.SizePrefix.DWORD]


@dataclass(kw_only=True)
class DungeonMasterGroupToggleAI(m.Message):
    MAJOR = 0x27
    MINOR = 0x2B
    DIRECTION = m.Direction.C2S

    targets: Annotated[list[m.ObjectId], m.SizePrefix.DWORD]


@dataclass(kw_only=True)
class DungeonMasterGroupImmortal(m.Message):
    MAJOR = 0x27
    MINOR = 0x32
    DIRECTION = m.Direction.C2S

    targets: Annotated[list[m.ObjectId], m.SizePrefix.DWORD]


@dataclass(kw_only=True)
class DungeonMasterGroupGotoPointTarget(m.Message):
    MAJOR = 0x27
    MINOR = 0x82
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    position: m.Vec3
    targets: Annotated[list[m.ObjectId], m.SizePrefix.DWORD]
