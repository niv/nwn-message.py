from dataclasses import dataclass, field
from typing import Annotated

from .. import message as m


@dataclass(kw_only=True)
class PartyList(m.Message):
    MAJOR = 0x0E
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    members: Annotated[list[m.ObjectId], m.SizePrefix.INT] = field(default_factory=list)


@dataclass(kw_only=True)
class PartyListAdd(m.Message):
    MAJOR = 0x0E
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    members: Annotated[list[m.ObjectId], m.SizePrefix.INT]


@dataclass(kw_only=True)
class PartyListRemove(m.Message):
    MAJOR = 0x0E
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    members: Annotated[list[m.ObjectId], m.SizePrefix.INT]


@dataclass(kw_only=True)
class PartyTransferObjectControl(m.Message):
    MAJOR = 0x0E
    MINOR = 0x0E
    DIRECTION = m.Direction.S2C

    controlling_player: m.Dword
    creature: m.ObjectId


@dataclass(kw_only=True)
class PartyGetList(m.Message):
    MAJOR = 0x0E
    MINOR = 0x02
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class PartyLeave(m.Message):
    MAJOR = 0x0E
    MINOR = 0x06
    DIRECTION = m.Direction.C2S

    creature: m.ObjectId


@dataclass(kw_only=True)
class PartyKick(m.Message):
    MAJOR = 0x0E
    MINOR = 0x07
    DIRECTION = m.Direction.C2S

    creature: m.ObjectId


@dataclass(kw_only=True)
class PartyTransferLeadership(m.Message):
    MAJOR = 0x0E
    MINOR = 0x08
    DIRECTION = m.Direction.C2S

    creature: m.ObjectId


@dataclass(kw_only=True)
class PartyInvite(m.Message):
    MAJOR = 0x0E
    MINOR = 0x09
    DIRECTION = m.Direction.C2S

    creature: m.ObjectId


@dataclass(kw_only=True)
class PartyIgnoreInvitation(m.Message):
    MAJOR = 0x0E
    MINOR = 0x0A
    DIRECTION = m.Direction.C2S

    creature: m.ObjectId


@dataclass(kw_only=True)
class PartyAcceptInvitation(m.Message):
    MAJOR = 0x0E
    MINOR = 0x0B
    DIRECTION = m.Direction.C2S

    creature: m.ObjectId


@dataclass(kw_only=True)
class PartyRejectInvitation(m.Message):
    MAJOR = 0x0E
    MINOR = 0x0C
    DIRECTION = m.Direction.C2S

    creature: m.ObjectId


@dataclass(kw_only=True)
class PartyKickHenchman(m.Message):
    MAJOR = 0x0E
    MINOR = 0x0D
    DIRECTION = m.Direction.C2S

    creature: m.ObjectId
