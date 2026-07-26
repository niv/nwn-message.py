from dataclasses import dataclass
from typing import Annotated

import nwn_message.message as m


@dataclass(kw_only=True)
class NuiCreateWindow(m.Message):
    MAJOR = 0x37
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    token: m.Int
    window_id: m.String
    type: m.Int
    resref: Annotated[m.ResRef, m.IfEq("type", 0)] = ""
    data: Annotated[m.Void | None, m.IfEq("type", 1)] = None


@dataclass(kw_only=True)
class NuiDestroyWindow(m.Message):
    MAJOR = 0x37
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    token: m.Int


@dataclass(kw_only=True)
class NuiEventEntry:
    token: m.Int
    event: m.String
    element: m.String
    array_index: m.Int
    payload: m.Void


@dataclass(kw_only=True)
class NuiEvents(m.Message):
    MAJOR = 0x37
    MINOR = 0x03
    DIRECTION = m.Direction.C2S

    events: Annotated[list[NuiEventEntry], m.SizePrefix.INT]


@dataclass(kw_only=True)
class NuiBindEntry:
    token: m.Int
    bind: m.String
    value: m.Void
    array_index: m.Int = 0


@dataclass(kw_only=True)
class NuiBinds(m.Message):
    MAJOR = 0x37
    MINOR = 0x04

    binds: Annotated[list[NuiBindEntry], m.SizePrefix.INT]


@dataclass(kw_only=True)
class NuiSetLayout(m.Message):
    MAJOR = 0x37
    MINOR = 0x05
    DIRECTION = m.Direction.S2C

    token: m.Int
    element: m.String
    data: m.Void
