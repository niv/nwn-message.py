from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class CharacterDownloadRequest(m.Message):
    MAJOR = 0x2B
    MINOR = 0x01
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class CharacterDownloadTransmit(m.Message):
    MAJOR = 0x2B
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    first_name: m.LocStr
    last_name: m.LocStr
    character_data: m.Void


@dataclass(kw_only=True)
class CharacterDownloadSavedOnServer(m.Message):
    MAJOR = 0x2B
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    character_name: m.String
    server_subdir: m.Bool
