from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class QuickChat(m.Message):
    MAJOR = 0x16
    MINOR = 0x00
    DIRECTION = m.Direction.S2C

    speaker: m.ObjectId
    sound_set_sound_id: m.Word


@dataclass(kw_only=True)
class QuickChatC2S(m.Message):
    MAJOR = 0x16
    MINOR = 0x00
    DIRECTION = m.Direction.C2S

    sound_set_sound_id: m.Word
