from typing import Annotated
from dataclasses import dataclass
from enum import IntEnum

from .. import message as m


class DevicePropertyType(IntEnum):
    INT = 1


@dataclass(kw_only=True)
class DeviceAdvertiseProperty(m.Message):
    MAJOR = 0x36
    MINOR = 0x01
    DIRECTION = m.Direction.C2S

    property: m.String
    type: Annotated[DevicePropertyType, m.MessageType.INT]
    value: m.Int


@dataclass(kw_only=True)
class DeviceEchoRequest(m.Message):
    MAJOR = 0x36
    MINOR = 0x02

    data: m.Void


@dataclass(kw_only=True)
class DeviceEchoResponse(m.Message):
    MAJOR = 0x36
    MINOR = 0x03

    data: m.Void
