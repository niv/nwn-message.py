from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class VoiceChatPlay(m.Message):
    MAJOR = 0x1A
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    object_id: m.ObjectId
    voiceset_id: m.Byte
