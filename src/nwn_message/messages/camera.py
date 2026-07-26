from dataclasses import dataclass
from enum import IntFlag
from typing import Annotated

from .. import message as m


class CameraChangeFlag(IntFlag):
    ANGLE = 0x01
    DISTANCE = 0x02
    PITCH = 0x04
    SMOOTH_TRANSLATION = 0x08


@dataclass(kw_only=True)
class CameraChangeLocation(m.Message):
    MAJOR = 0x10
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    flags: m.Byte
    angle: Annotated[m.Float, m.IfFlag("flags", CameraChangeFlag.ANGLE)]
    distance: Annotated[m.Float, m.IfFlag("flags", CameraChangeFlag.DISTANCE)]
    pitch: Annotated[m.Float, m.IfFlag("flags", CameraChangeFlag.PITCH)]
    smooth_translation: Annotated[
        m.Int, m.IfFlag("flags", CameraChangeFlag.SMOOTH_TRANSLATION)
    ]


@dataclass(kw_only=True)
class CameraSetMode(m.Message):
    MAJOR = 0x10
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    mode: m.Byte


@dataclass(kw_only=True)
class CameraStore(m.Message):
    MAJOR = 0x10
    MINOR = 0x03
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class CameraRestore(m.Message):
    MAJOR = 0x10
    MINOR = 0x04
    DIRECTION = m.Direction.S2C


@dataclass(kw_only=True)
class CameraSetHeight(m.Message):
    MAJOR = 0x10
    MINOR = 0x05
    DIRECTION = m.Direction.S2C

    height: m.Float


@dataclass(kw_only=True)
class CameraLockPitch(m.Message):
    MAJOR = 0x10
    MINOR = 0x06
    DIRECTION = m.Direction.S2C

    lock: m.Bool


@dataclass(kw_only=True)
class CameraLockDist(m.Message):
    MAJOR = 0x10
    MINOR = 0x07
    DIRECTION = m.Direction.S2C

    lock: m.Bool


@dataclass(kw_only=True)
class CameraLockYaw(m.Message):
    MAJOR = 0x10
    MINOR = 0x08
    DIRECTION = m.Direction.S2C

    lock: m.Bool


@dataclass(kw_only=True)
class CameraSetLimits(m.Message):
    MAJOR = 0x10
    MINOR = 0x09
    DIRECTION = m.Direction.S2C

    min_pitch: m.Float
    max_pitch: m.Float
    min_dist: m.Float
    max_dist: m.Float


@dataclass(kw_only=True)
class CameraAttach(m.Message):
    MAJOR = 0x10
    MINOR = 0x0A
    DIRECTION = m.Direction.S2C

    target: m.ObjectId
    find_clear_view: m.Bool


@dataclass(kw_only=True)
class CameraAttachRevert(m.Message):
    MAJOR = 0x10
    MINOR = 0x0B
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class CameraSetFlags(m.Message):
    MAJOR = 0x10
    MINOR = 0x0C
    DIRECTION = m.Direction.S2C

    flags: m.Int
