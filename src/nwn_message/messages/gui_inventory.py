from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class GuiInventoryStatusC2S(m.Message):
    MAJOR = 0x0D
    MINOR = 0x01
    DIRECTION = m.Direction.C2S

    active: m.Bool
    inventory: m.ObjectId


@dataclass(kw_only=True)
class GuiInventoryStatus(m.Message):
    MAJOR = 0x0D
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    active: m.Bool
    inventory: m.ObjectId


@dataclass(kw_only=True)
class GuiInventorySelectPanelC2S(m.Message):
    MAJOR = 0x0D
    MINOR = 0x02
    DIRECTION = m.Direction.C2S

    panel: m.Byte
    player_panel: m.Bool


@dataclass(kw_only=True)
class GuiInventorySelectPanel(m.Message):
    MAJOR = 0x0D
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    panel: m.Byte
