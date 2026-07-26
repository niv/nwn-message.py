from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class MapPinPinEnabled(m.Message):
    MAJOR = 0x20
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    map_pin: m.ObjectId
    enabled: m.Bool


@dataclass(kw_only=True)
class MapPinSetMapPinAt(m.Message):
    MAJOR = 0x20
    MINOR = 0x02
    DIRECTION = m.Direction.C2S

    position: m.Vec3
    note: m.String


@dataclass(kw_only=True)
class MapPinDestroyMapPin(m.Message):
    MAJOR = 0x20
    MINOR = 0x03
    DIRECTION = m.Direction.C2S

    reference_number: m.Int


@dataclass(kw_only=True)
class MapPinReferenceNumber(m.Message):
    MAJOR = 0x20
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    position: m.Vec3
    note: m.String
    reference_number: m.Dword


@dataclass(kw_only=True)
class MapPinChangePin(m.Message):
    MAJOR = 0x20
    MINOR = 0x05
    DIRECTION = m.Direction.C2S

    position: m.Vec3
    note: m.String
    reference_number: m.Int


@dataclass(kw_only=True)
class MapPinCreated(m.Message):
    MAJOR = 0x20
    MINOR = 0x06
    DIRECTION = m.Direction.S2C

    map_pin: m.ObjectId
    position: m.Vec3
    note: m.LocStr
    enabled: m.Bool
