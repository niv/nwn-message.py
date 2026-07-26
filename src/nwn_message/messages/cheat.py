from dataclasses import dataclass
from enum import IntFlag
from typing import Annotated

from .. import message as m


class CheatCastSpellFlag(IntFlag):
    TARGET_OBJECT = 0x01
    TARGET_POSITION = 0x02
    SPONTANEOUSLY_CAST = 0x04


@dataclass(kw_only=True)
class CheatMoveToArea(m.Message):
    MAJOR = 0x0F
    MINOR = 0x01
    DIRECTION = m.Direction.C2S

    area_tag: m.String
    position: m.Vec3


@dataclass(kw_only=True)
class CheatResurrect(m.Message):
    MAJOR = 0x0F
    MINOR = 0x02
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class CheatCastSpell(m.Message):
    MAJOR = 0x0F
    MINOR = 0x03
    DIRECTION = m.Direction.C2S

    spell_id: m.Dword
    multiclass: m.Byte
    domain_level: m.Byte
    metatype: m.Byte
    flags: m.Byte
    target_object_id: Annotated[
        m.ObjectId, m.IfFlag("flags", CheatCastSpellFlag.TARGET_OBJECT)
    ]
    target_position: Annotated[
        m.Vec3, m.IfFlag("flags", CheatCastSpellFlag.TARGET_POSITION)
    ]


@dataclass(kw_only=True)
class CheatInvulnerability(m.Message):
    MAJOR = 0x0F
    MINOR = 0x04
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class CheatKill(m.Message):
    MAJOR = 0x0F
    MINOR = 0x07
    DIRECTION = m.Direction.C2S

    effector: m.ObjectId
    target: m.ObjectId


@dataclass(kw_only=True)
class CheatRunScript(m.Message):
    MAJOR = 0x0F
    MINOR = 0x08
    DIRECTION = m.Direction.C2S

    script_name: m.String
    self_object: m.ObjectId


@dataclass(kw_only=True)
class CheatToggleCombatDebugging(m.Message):
    MAJOR = 0x0F
    MINOR = 0x09
    DIRECTION = m.Direction.C2S

    enabled: m.Bool


@dataclass(kw_only=True)
class CheatPlayVisualEffect(m.Message):
    MAJOR = 0x0F
    MINOR = 0x0A
    DIRECTION = m.Direction.C2S

    creature: m.ObjectId
    effect_id: m.Word
    duration: m.Float
    position: m.Vec3


@dataclass(kw_only=True)
class CheatDoNastyC2S(m.Message):
    MAJOR = 0x0F
    MINOR = 0x0B
    DIRECTION = m.Direction.C2S

    trigger: m.Bool


@dataclass(kw_only=True)
class CheatDoNasty(m.Message):
    MAJOR = 0x0F
    MINOR = 0x0B
    DIRECTION = m.Direction.S2C

    creature: m.ObjectId


@dataclass(kw_only=True)
class CheatPonyRideC2S(m.Message):
    MAJOR = 0x0F
    MINOR = 0x0C
    DIRECTION = m.Direction.C2S

    trigger: m.Bool


@dataclass(kw_only=True)
class CheatPonyRide(m.Message):
    MAJOR = 0x0F
    MINOR = 0x0C
    DIRECTION = m.Direction.S2C

    creature: m.ObjectId
    enabled: m.Bool


@dataclass(kw_only=True)
class CheatRainOfCowsC2S(m.Message):
    MAJOR = 0x0F
    MINOR = 0x0D
    DIRECTION = m.Direction.C2S

    trigger: m.Bool


@dataclass(kw_only=True)
class CheatRainOfCows(m.Message):
    MAJOR = 0x0F
    MINOR = 0x0D
    DIRECTION = m.Direction.S2C

    creature: m.ObjectId
    enabled: m.Bool


@dataclass(kw_only=True)
class CheatSummonNasty(m.Message):
    MAJOR = 0x0F
    MINOR = 0x0E
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    appearance_type: m.Byte
    template: m.ResRef


@dataclass(kw_only=True)
class CheatToggleFloatyEffects(m.Message):
    MAJOR = 0x0F
    MINOR = 0x0F
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class CheatToggleNetworkProfiler(m.Message):
    MAJOR = 0x0F
    MINOR = 0x10
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class CheatShowServerMem(m.Message):
    MAJOR = 0x0F
    MINOR = 0x11
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class CheatLevelUp(m.Message):
    MAJOR = 0x0F
    MINOR = 0x12
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class CheatSaveTest(m.Message):
    MAJOR = 0x0F
    MINOR = 0x13
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class CheatTimeStopTest(m.Message):
    MAJOR = 0x0F
    MINOR = 0x14
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class CheatDebugModeC2S(m.Message):
    MAJOR = 0x0F
    MINOR = 0x15
    DIRECTION = m.Direction.C2S

    enabled: m.Bool


@dataclass(kw_only=True)
class CheatDebugMode(m.Message):
    MAJOR = 0x0F
    MINOR = 0x15
    DIRECTION = m.Direction.S2C

    enabled: m.Bool


@dataclass(kw_only=True)
class CheatToggleMovementSpeedDebugging(m.Message):
    MAJOR = 0x0F
    MINOR = 0x16
    DIRECTION = m.Direction.C2S

    enabled: m.Bool


@dataclass(kw_only=True)
class CheatLoadQuickBar(m.Message):
    MAJOR = 0x0F
    MINOR = 0x17
    DIRECTION = m.Direction.C2S

    filename: m.String


@dataclass(kw_only=True)
class CheatSaveQuickBar(m.Message):
    MAJOR = 0x0F
    MINOR = 0x18
    DIRECTION = m.Direction.C2S

    filename: m.String


@dataclass(kw_only=True)
class CheatPlayerPathfindRule(m.Message):
    MAJOR = 0x0F
    MINOR = 0x19
    DIRECTION = m.Direction.C2S

    pathfind_rule: m.Byte


@dataclass(kw_only=True)
class CheatComputeSafeLocation(m.Message):
    MAJOR = 0x0F
    MINOR = 0x1A
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class CheatEnableScriptDebugger(m.Message):
    MAJOR = 0x0F
    MINOR = 0x1B
    DIRECTION = m.Direction.C2S

    enabled: m.Byte


@dataclass(kw_only=True)
class CheatToggleHitDieDebugging(m.Message):
    MAJOR = 0x0F
    MINOR = 0x1C
    DIRECTION = m.Direction.C2S

    enabled: m.Bool


@dataclass(kw_only=True)
class CheatRunScriptChunk(m.Message):
    MAJOR = 0x0F
    MINOR = 0x1D
    DIRECTION = m.Direction.C2S

    script_chunk: m.String
    self_object: m.ObjectId
    wrap_main: m.Bool
