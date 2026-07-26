from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class GuiPartyBarPanelButtonFlash(m.Message):
    MAJOR = 0x2E
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    button: m.Byte
    enable_flash: m.Bool
