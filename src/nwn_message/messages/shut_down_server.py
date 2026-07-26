from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class ShutDownServerC2S(m.Message):
    MAJOR = 0x2F
    MINOR = 0x00
    DIRECTION = m.Direction.C2S

    forced: m.Bool


@dataclass(kw_only=True)
class ShutDownServerS2C(m.Message):
    MAJOR = 0x2F
    MINOR = 0x00
    DIRECTION = m.Direction.S2C

    time_left: m.Dword
