from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class PortalActivatePortal(m.Message):
    MAJOR = 0x2A
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    ip_address: m.String
    password: m.String
    waypoint_tag: m.String
    seamless: m.Bool


@dataclass(kw_only=True)
class PortalSuccess(m.Message):
    MAJOR = 0x2A
    MINOR = 0x02
    DIRECTION = m.Direction.C2S

    success: m.Bool
