from dataclasses import dataclass

import nwn_message.message as m


@dataclass(kw_only=True)
class AudioStreamEvent(m.Message):
    MAJOR = 0x40
    MINOR = 0x01
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class AudioStreamStart(m.Message):
    MAJOR = 0x40
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    identifier: m.Dword
    filename: m.String
    looping: m.Bool
    fade_in_time: m.Dword
    seek_offset: m.Float
    volume: m.Float


@dataclass(kw_only=True)
class AudioStreamStop(m.Message):
    MAJOR = 0x40
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    identifier: m.Dword
    milliseconds: m.Dword


@dataclass(kw_only=True)
class AudioStreamSetPaused(m.Message):
    MAJOR = 0x40
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    identifier: m.Dword
    paused: m.Bool
    fade_time: m.Dword


@dataclass(kw_only=True)
class AudioStreamSetVolume(m.Message):
    MAJOR = 0x40
    MINOR = 0x05
    DIRECTION = m.Direction.S2C

    identifier: m.Dword
    volume: m.Float
    fade_time: m.Dword


@dataclass(kw_only=True)
class AudioStreamSeek(m.Message):
    MAJOR = 0x40
    MINOR = 0x06
    DIRECTION = m.Direction.S2C

    identifier: m.Dword
    offset: m.Float
