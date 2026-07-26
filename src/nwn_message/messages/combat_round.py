from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class CombatRoundStarted(m.Message):
    MAJOR = 0x13
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    started: m.Byte
