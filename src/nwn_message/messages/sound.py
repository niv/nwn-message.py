from dataclasses import dataclass
from typing import Annotated

from .. import message as m


@dataclass(kw_only=True)
class Sound:
    object_id: m.ObjectId
    active: m.Bool
    positional: m.Bool
    looping: m.Bool
    volume: m.Byte
    volume_variation: m.Byte
    time_of_day: m.Byte
    pitch_variation: m.Float
    hours: m.Dword
    priority: m.Byte
    interval: m.Dword
    interval_variance: m.Dword
    min_distance: m.Float
    max_distance: m.Float
    continuous: m.Bool
    random: m.Bool
    random_position: m.Bool
    random_x_range: m.Float
    random_y_range: m.Float
    position: m.Vec3
    sounds: Annotated[list[m.ResRef], m.SizePrefix.WORD]


@dataclass(kw_only=True)
class SoundPlay3D(m.Message):
    MAJOR = 0x17
    MINOR = 0x01

    # Legacy/unused in current EE handlers


@dataclass(kw_only=True)
class SoundObjectPlay(m.Message):
    MAJOR = 0x17
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    sound_object: m.ObjectId


@dataclass(kw_only=True)
class SoundObjectStop(m.Message):
    MAJOR = 0x17
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    sound_object: m.ObjectId


@dataclass(kw_only=True)
class SoundObjectChangeVolume(m.Message):
    MAJOR = 0x17
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    sound_object: m.ObjectId
    volume: m.Int


@dataclass(kw_only=True)
class SoundObjectChangePosition(m.Message):
    MAJOR = 0x17
    MINOR = 0x05
    DIRECTION = m.Direction.S2C

    sound_object: m.ObjectId
    position: m.Vec3


@dataclass(kw_only=True)
class SoundObjectCreate(m.Message):
    MAJOR = 0x17
    MINOR = 0x06
    DIRECTION = m.Direction.S2C

    sound_object: m.ObjectId
    area: m.ObjectId
    sound: Sound


@dataclass(kw_only=True)
class SoundObjectDestroy(m.Message):
    MAJOR = 0x17
    MINOR = 0x07
    DIRECTION = m.Direction.S2C

    sound_object: m.ObjectId
