from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class BarterRqstStartBarter(m.Message):
    MAJOR = 0x23
    MINOR = 0x01
    DIRECTION = m.Direction.C2S

    target: m.ObjectId
    item: m.ObjectId


@dataclass(kw_only=True)
class BarterAcptStartBarter(m.Message):
    MAJOR = 0x23
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    initiator_creature: m.ObjectId
    recipient_creature: m.ObjectId


@dataclass(kw_only=True)
class BarterRqstCloseBarter(m.Message):
    MAJOR = 0x23
    MINOR = 0x03
    DIRECTION = m.Direction.C2S

    close: m.Bool


@dataclass(kw_only=True)
class BarterAcptCloseBarter(m.Message):
    MAJOR = 0x23
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    accepted: m.Bool


@dataclass(kw_only=True)
class BarterRqstAddItem(m.Message):
    MAJOR = 0x23
    MINOR = 0x05
    DIRECTION = m.Direction.C2S

    item: m.ObjectId
    x: m.Byte
    y: m.Byte


@dataclass(kw_only=True)
class BarterRqstRemoveItem(m.Message):
    MAJOR = 0x23
    MINOR = 0x06
    DIRECTION = m.Direction.C2S

    item: m.ObjectId
    x: m.Byte
    y: m.Byte


@dataclass(kw_only=True)
class BarterRqstLockList(m.Message):
    MAJOR = 0x23
    MINOR = 0x07
    DIRECTION = m.Direction.C2S

    locked: m.Bool


@dataclass(kw_only=True)
class BarterAcptLockList(m.Message):
    MAJOR = 0x23
    MINOR = 0x08
    DIRECTION = m.Direction.S2C

    initiator: m.Bool
    locked: m.Bool


@dataclass(kw_only=True)
class BarterRqstAcceptTrade(m.Message):
    MAJOR = 0x23
    MINOR = 0x09
    DIRECTION = m.Direction.C2S

    accept: m.Bool


@dataclass(kw_only=True)
class BarterAcptAcceptTrade(m.Message):
    MAJOR = 0x23
    MINOR = 0x0A
    DIRECTION = m.Direction.S2C

    initiator: m.Bool
    accept: m.Bool


@dataclass(kw_only=True)
class BarterReject(m.Message):
    MAJOR = 0x23
    MINOR = 0x0B
    DIRECTION = m.Direction.S2C

    message: m.Byte
    flags: m.Byte
    item: m.ObjectId


@dataclass(kw_only=True)
class BarterWindow(m.Message):
    MAJOR = 0x23
    MINOR = 0x0C
    DIRECTION = m.Direction.C2S

    open: m.Bool


@dataclass(kw_only=True)
class BarterRqstMoveItem(m.Message):
    MAJOR = 0x23
    MINOR = 0x0D
    DIRECTION = m.Direction.C2S

    item: m.ObjectId
    x: m.Byte
    y: m.Byte
