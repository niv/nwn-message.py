from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class GuiCharacterSheetStatus(m.Message):
    MAJOR = 0x15
    MINOR = 0x01

    active_panel: m.Char
    creature: m.ObjectId


@dataclass(kw_only=True)
class GuiCharacterSheetNotPermitted(m.Message):
    MAJOR = 0x15
    MINOR = 0x02

    creature: m.ObjectId
