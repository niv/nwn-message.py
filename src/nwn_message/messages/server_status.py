from dataclasses import dataclass, field
from typing import Annotated

from .. import message as m


@dataclass(kw_only=True)
class ServerStatusRequest(m.Message):
    MAJOR = 0x01
    MINOR = 0x00
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class ServerStatusModuleLoaded(m.Message):
    MAJOR = 0x01
    MINOR = 0x01
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class ServerStatusIdle(m.Message):
    MAJOR = 0x01
    MINOR = 0x02
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class NWSync:
    @dataclass(kw_only=True)
    class Manifest:
        hash: m.String
        flags: m.Byte
        language_id: m.Byte

    primary_manifest: m.String
    urls: Annotated[list[m.String], m.SizePrefix.BYTE]
    manifests: Annotated[list[Manifest], m.SizePrefix.BYTE]


@dataclass(kw_only=True)
class ServerStatusModuleRunning(m.Message):
    MAJOR = 0x01
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    module_id: m.String = ""  # always empty
    nwsync: Annotated[NWSync | None, m.BoolPrefix()] = None
    alt_tlk: m.String = ""
    resource_name: m.String = ""
    haks: Annotated[list[m.ResRef], m.SizePrefix.BYTE] = field(default_factory=list)
