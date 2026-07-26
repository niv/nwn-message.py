from dataclasses import dataclass, field
from enum import IntEnum
from typing import Annotated

from . import message as m


class LerpTimerType(IntEnum):
    NONE = -1
    REAL_TIME = 0
    WORLD_TIME = 1


class LerpType(IntEnum):
    NONE = 0
    LINEAR = 1
    SMOOTHSTEP = 2
    INVERSE_SMOOTHSTEP = 3
    EASE_IN = 4
    EASE_OUT = 5
    QUADRATIC = 6
    SMOOTHERSTEP = 7


class LerpFlags(IntEnum):
    DEFAULT = 0
    BOUNCE = 1


@dataclass(kw_only=True)
class LerpFloat:
    value_to: m.Float = 1.0
    timer_type: Annotated[LerpTimerType, m.MessageType.INT] = LerpTimerType.REAL_TIME
    lerp_type: Annotated[LerpType, m.MessageType.INT] = LerpType.NONE
    value_from: Annotated[m.Float, m.IfNotEq("lerp_type", LerpType.NONE)] = 0.0
    duration: Annotated[m.Float, m.IfNotEq("lerp_type", LerpType.NONE)] = 0.0
    progress: Annotated[m.Float, m.IfNotEq("lerp_type", LerpType.NONE)] = 0.0
    flags: Annotated[
        LerpFlags, m.IfNotEq("lerp_type", LerpType.NONE), m.MessageType.INT
    ] = LerpFlags.DEFAULT
    repeats_remaining: Annotated[m.Int, m.IfNotEq("lerp_type", LerpType.NONE)] = 0


@dataclass(kw_only=True)
class LerpVector:
    x: LerpFloat
    y: LerpFloat
    z: LerpFloat


@dataclass(kw_only=True)
class VisualTransformData:
    @dataclass(kw_only=True)
    class Update:
        scope: m.Int
        identity: m.Bool
        scale: Annotated[LerpVector, m.IfNotEq("identity", True)]
        rotate: Annotated[LerpVector, m.IfNotEq("identity", True)]
        translate: Annotated[LerpVector, m.IfNotEq("identity", True)]
        animation_speed: Annotated[LerpFloat, m.IfNotEq("identity", True)]

    known_indices: Annotated[list[m.Int], m.SizePrefix.INT] = field(
        default_factory=list
    )
    total_updates: Annotated[list[Update], m.SizePrefix.INT] = field(
        default_factory=list
    )
