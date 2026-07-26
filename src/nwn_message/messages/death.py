from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class DeathRespawn(m.Message):
    MAJOR = 0x25
    MINOR = 0x01
    DIRECTION = m.Direction.C2S
