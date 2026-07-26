from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class GuiContainerStatus(m.Message):
    MAJOR = 0x19
    MINOR = 0x01
    DIRECTION = m.Direction.C2S

    container: m.ObjectId


@dataclass(kw_only=True)
class GuiContainerStatusS2C(m.Message):
    MAJOR = 0x19
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    container: m.ObjectId
    open_in_own_panel: m.Bool


@dataclass(kw_only=True)
class GuiContainerNextPage(m.Message):
    MAJOR = 0x19
    MINOR = 0x02
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class GuiContainerPreviousPage(m.Message):
    MAJOR = 0x19
    MINOR = 0x03
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class GuiContainerSelectPage(m.Message):
    MAJOR = 0x19
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    page: m.Byte
