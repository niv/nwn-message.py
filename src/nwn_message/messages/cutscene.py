from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class CutsceneStatus(m.Message):
    MAJOR = 0x33
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    active: m.Bool
    left_mouse_button_enabled: m.Bool


@dataclass(kw_only=True)
class CutsceneCancel(m.Message):
    MAJOR = 0x33
    MINOR = 0x02
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class CutsceneFadeToBlack(m.Message):
    MAJOR = 0x33
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    speed: m.Float


@dataclass(kw_only=True)
class CutsceneFadeFromBlack(m.Message):
    MAJOR = 0x33
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    speed: m.Float


@dataclass(kw_only=True)
class CutsceneStopFade(m.Message):
    MAJOR = 0x33
    MINOR = 0x05
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class CutsceneBlackScreen(m.Message):
    MAJOR = 0x33
    MINOR = 0x06
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class CutsceneHideGui(m.Message):
    MAJOR = 0x33
    MINOR = 0x07
    DIRECTION = m.Direction.S2C

    hide: m.Bool
