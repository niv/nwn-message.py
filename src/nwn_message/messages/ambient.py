from dataclasses import dataclass

from .. import message as m


@dataclass(kw_only=True)
class AmbientMusicPlay(m.Message):
    MAJOR = 0x28
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    play: m.Bool


@dataclass(kw_only=True)
class AmbientMusicSetDelay(m.Message):
    MAJOR = 0x28
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    delay: m.Int


@dataclass(kw_only=True)
class AmbientMusicChange(m.Message):
    MAJOR = 0x28
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    day: m.Bool
    track: m.Int


@dataclass(kw_only=True)
class AmbientBattleMusicPlay(m.Message):
    MAJOR = 0x28
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    play: m.Bool


@dataclass(kw_only=True)
class AmbientBattleMusicChange(m.Message):
    MAJOR = 0x28
    MINOR = 0x05
    DIRECTION = m.Direction.S2C

    track: m.Int


@dataclass(kw_only=True)
class AmbientSoundPlay(m.Message):
    MAJOR = 0x28
    MINOR = 0x06
    DIRECTION = m.Direction.S2C

    play: m.Bool


@dataclass(kw_only=True)
class AmbientSoundChange(m.Message):
    MAJOR = 0x28
    MINOR = 0x07
    DIRECTION = m.Direction.S2C

    day: m.Bool
    track: m.Int


@dataclass(kw_only=True)
class AmbientSoundVolume(m.Message):
    MAJOR = 0x28
    MINOR = 0x08
    DIRECTION = m.Direction.S2C

    day: m.Bool
    volume: m.Int
