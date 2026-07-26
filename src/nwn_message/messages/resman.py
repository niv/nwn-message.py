from typing import Annotated
from dataclasses import dataclass
from enum import IntFlag, IntEnum

from .. import message as m


class ResmanOverrideAction(IntEnum):
    STORE = ord("S")
    REMOVE = ord("C")


@dataclass(kw_only=True)
class ResmanOverride(m.Message):
    MAJOR = 0x34
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    action: Annotated[ResmanOverrideAction, m.MessageType.CHAR]
    restype: m.Short
    name: m.ResRef
    new_name: Annotated[m.ResRef, m.IfEq("action", ResmanOverrideAction.STORE)] = ""


@dataclass(kw_only=True)
class ResmanTlkOverride(m.Message):
    MAJOR = 0x34
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    strref: m.Dword
    value: m.String


@dataclass(kw_only=True)
class ResmanTlkOverrideList(m.Message):
    MAJOR = 0x34
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    overrides: Annotated[list[tuple[m.Dword, m.String]], m.SizePrefix.DWORD]


@dataclass(kw_only=True)
class ResmanReloadResources(m.Message):
    MAJOR = 0x34
    MINOR = 0x04

    class Bits(IntFlag):
        RELOAD_RULES = 0x1
        RELOAD_TEXTURES = 0x2
        RELOAD_CURSORS = 0x4
        RELOAD_MODELS = 0x8
        RELOAD_TLK = 0x10
        RELOAD_PALETTES = 0x20
        RELOAD_SHADERS = 0x40
        RELOAD_WALKABLE_MATERIALS = 0x80
        DUMP_RESOURCES = 0x100
        RELOAD_NUI = 0x200
        RELOAD_TILESETS = 0x400

    bits: Annotated[Bits, m.MessageType.DWORD]


class ResourceOp(IntEnum):
    STORE = 0
    DELETE = 1


class ResourceOpFlag(IntFlag):
    STORE_NWSYNC = 0x1


@dataclass(kw_only=True)
class ResmanSaveResources(m.Message):
    MAJOR = 0x34
    MINOR = 0x05
    DIRECTION = m.Direction.S2C

    @dataclass(kw_only=True)
    class Resource:
        name: m.ResRef
        restype: m.Short
        operation: Annotated[ResourceOp, m.Dword]

        @dataclass(kw_only=True)
        class Store:
            flags: m.Dword
            data: m.Void
            sha1: Annotated[m.SHA1, m.IfFlag("flags", ResourceOpFlag.STORE_NWSYNC)]

        store: Annotated[Store, m.IfFlag("operation", ResourceOp.STORE)]

    resources: Annotated[list[Resource], m.SizePrefix.DWORD]


@dataclass(kw_only=True)
class ResmanResourcesReceived(m.Message):
    MAJOR = 0x34
    MINOR = 0x06
    DIRECTION = m.Direction.C2S

    opaque: m.Dword
    resources: Annotated[list[m.Byte], m.SizePrefix.WORD]
