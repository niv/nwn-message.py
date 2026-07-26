from typing import Annotated
from dataclasses import dataclass
from enum import Flag, IntEnum

from .. import message as m

INVALID_OBJECT_ID = 0x7F000000


class ToggleMode(IntEnum):
    DETECT = 0
    STEALTH = 1
    PARRY = 2
    POWER_ATTACK = 3
    IMPROVED_POWER_ATTACK = 4
    COUNTERSPELL = 5
    FLURRY_OF_BLOWS = 6
    RAPID_SHOT = 7
    EXPERTISE = 8
    IMPROVED_EXPERTISE = 9
    DEFENSIVE_CAST = 10
    DIRTY_FIGHTING = 11
    DEFENSIVE_STANCE = 12


class CastSpellFlags(Flag):
    HAS_TARGET = 0x1
    HAS_POSITION = 0x2
    SPONTANEOUS = 0x4


@dataclass(kw_only=True)
class InputWalkToWayPoint(m.Message):
    MAJOR = 0x06
    MINOR = 0x01
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    position: m.Vec3
    event_number: m.Byte
    run: m.Bool
    client_moving: m.Bool
    move_mode: m.Byte
    clicked_on: m.ObjectId


@dataclass(kw_only=True)
class InputAttack(m.Message):
    MAJOR = 0x06
    MINOR = 0x02
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class InputChangeDoorState(m.Message):
    MAJOR = 0x06
    MINOR = 0x03
    DIRECTION = m.Direction.C2S

    door: m.ObjectId
    animation: m.Word


@dataclass(kw_only=True)
class InputPlayAnimation(m.Message):
    MAJOR = 0x06
    MINOR = 0x04
    DIRECTION = m.Direction.C2S

    animation: m.Word
    target: m.ObjectId
    position: m.Vec3
    duration: m.Float


@dataclass(kw_only=True)
class InputExamine(m.Message):
    MAJOR = 0x06
    MINOR = 0x05
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class InputUseFeat(m.Message):
    MAJOR = 0x06
    MINOR = 0x06
    DIRECTION = m.Direction.C2S

    feat: m.Word
    sub_feat: m.Word
    target: m.ObjectId
    position: Annotated[m.Vec3, m.IfEq("target", INVALID_OBJECT_ID)]


@dataclass(kw_only=True)
class InputUseSkill(m.Message):
    MAJOR = 0x06
    MINOR = 0x07
    DIRECTION = m.Direction.C2S

    skill: m.Byte
    sub_skill: m.Byte
    target: m.ObjectId
    position: m.Vec3


@dataclass(kw_only=True)
class InputDialog(m.Message):
    MAJOR = 0x06
    MINOR = 0x08
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class InputUseItem(m.Message):
    MAJOR = 0x06
    MINOR = 0x09
    DIRECTION = m.Direction.C2S

    item: m.ObjectId
    active_property_index: m.Byte
    sub_property_index: Annotated[m.Byte, m.BoolPrefix()]
    target: Annotated[m.ObjectId, m.BoolPrefix()]
    position: Annotated[m.Vec3, m.BoolPrefix()]


@dataclass(kw_only=True)
class InputToggleMode(m.Message):
    MAJOR = 0x06
    MINOR = 0x0A
    DIRECTION = m.Direction.C2S

    mode: Annotated[ToggleMode, m.MessageType.BYTE]
    target: Annotated[m.ObjectId, m.IfEq("mode", ToggleMode.COUNTERSPELL)]


@dataclass(kw_only=True)
class InputUseObject(m.Message):
    MAJOR = 0x06
    MINOR = 0x0B
    DIRECTION = m.Direction.C2S

    target: m.ObjectId
    close_inventory: m.Bool
    left_click: m.Bool


@dataclass(kw_only=True)
class InputUnlockObject(m.Message):
    MAJOR = 0x06
    MINOR = 0x0C
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class InputRest(m.Message):
    MAJOR = 0x06
    MINOR = 0x0D
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class InputLockObject(m.Message):
    MAJOR = 0x06
    MINOR = 0x0E
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class InputStopDragMode(m.Message):
    MAJOR = 0x06
    MINOR = 0x0F
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class InputMemorizeSpell(m.Message):
    MAJOR = 0x06
    MINOR = 0x10
    DIRECTION = m.Direction.C2S

    multi_class: m.Byte
    spell_id: m.Dword
    spell_slot: m.Byte
    domain_level: m.Byte
    meta_type: m.Byte


@dataclass(kw_only=True)
class InputUnMemorizeSpell(m.Message):
    MAJOR = 0x06
    MINOR = 0x11
    DIRECTION = m.Direction.C2S

    multi_class: m.Byte
    spell_level: m.Byte
    spell_slot: m.Byte


@dataclass(kw_only=True)
class InputCastSpell(m.Message):
    MAJOR = 0x06
    MINOR = 0x12
    DIRECTION = m.Direction.C2S

    spell_id: m.Dword
    multi_class: m.Byte
    domain_level: m.Byte
    meta_type: m.Byte
    flags: Annotated[CastSpellFlags, m.MessageType.BYTE]
    target: Annotated[m.ObjectId, m.IfFlag("flags", CastSpellFlags.HAS_TARGET)]
    position: Annotated[m.Vec3, m.IfFlag("flags", CastSpellFlags.HAS_POSITION)]
    spell_target_type: m.Word


@dataclass(kw_only=True)
class InputPossessFamiliar(m.Message):
    MAJOR = 0x06
    MINOR = 0x13
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class InputCancelAction(m.Message):
    MAJOR = 0x06
    MINOR = 0x14
    DIRECTION = m.Direction.C2S

    action_id: m.Word
    group_id: m.Word


@dataclass(kw_only=True)
class InputGetObjectDebugInfo(m.Message):
    MAJOR = 0x06
    MINOR = 0x15
    DIRECTION = m.Direction.C2S

    target: m.ObjectId


@dataclass(kw_only=True)
class InputMergeItem(m.Message):
    MAJOR = 0x06
    MINOR = 0x16
    DIRECTION = m.Direction.C2S

    target_item: m.ObjectId
    source_item: m.ObjectId


@dataclass(kw_only=True)
class InputSplitItem(m.Message):
    MAJOR = 0x06
    MINOR = 0x17
    DIRECTION = m.Direction.C2S

    item: m.ObjectId
    count: m.Word


@dataclass(kw_only=True)
class InputTogglePauseRequest(m.Message):
    MAJOR = 0x06
    MINOR = 0x18
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class InputSetPauseRequest(m.Message):
    MAJOR = 0x06
    MINOR = 0x19
    DIRECTION = m.Direction.C2S

    pause: m.Bool


@dataclass(kw_only=True)
class InputAlwaysRun(m.Message):
    MAJOR = 0x06
    MINOR = 0x1A
    DIRECTION = m.Direction.C2S

    always_run: m.Bool


@dataclass(kw_only=True)
class InputAssociateCommand(m.Message):
    MAJOR = 0x06
    MINOR = 0x1B
    DIRECTION = m.Direction.C2S

    associate: m.ObjectId
    command: m.Int


@dataclass(kw_only=True)
class InputTurnOnSpot(m.Message):
    MAJOR = 0x06
    MINOR = 0x1C
    DIRECTION = m.Direction.C2S

    direction_x: m.Float
    direction_y: m.Float


@dataclass(kw_only=True)
class InputDriveControl(m.Message):
    MAJOR = 0x06
    MINOR = 0x1D
    DIRECTION = m.Direction.C2S

    x: m.Float
    y: m.Float
    area: m.ObjectId
    bearing: Annotated[m.Word, m.Bits(12)]
    pathfind_event_number: m.Byte
    drive_flags: m.Byte


@dataclass(kw_only=True)
class InputCancelPolymorph(m.Message):
    MAJOR = 0x06
    MINOR = 0x1E
    DIRECTION = m.Direction.C2S

    creature: m.ObjectId


@dataclass(kw_only=True)
class InputExportRequest(m.Message):
    MAJOR = 0x06
    MINOR = 0x1F
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class InputQuickSave(m.Message):
    MAJOR = 0x06
    MINOR = 0x20
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class InputAbortDriveControl(m.Message):
    MAJOR = 0x06
    MINOR = 0x21
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class InputCancelGuiTimingEvent(m.Message):
    MAJOR = 0x06
    MINOR = 0x22
    DIRECTION = m.Direction.C2S


@dataclass(kw_only=True)
class InputCastSpellLikeAbility(m.Message):
    MAJOR = 0x06
    MINOR = 0x23
    DIRECTION = m.Direction.C2S

    spell_id: m.Dword
    caster_level: m.Byte
    flags: Annotated[CastSpellFlags, m.MessageType.BYTE]
    target: Annotated[m.ObjectId, m.IfFlag("flags", CastSpellFlags.HAS_TARGET)]
    position: Annotated[m.Vec3, m.IfFlag("flags", CastSpellFlags.HAS_POSITION)]


@dataclass(kw_only=True)
class InputBroadcastAssociateCommand(m.Message):
    MAJOR = 0x06
    MINOR = 0x24
    DIRECTION = m.Direction.C2S

    command: m.Int


@dataclass(kw_only=True)
class InputTargetSelected(m.Message):
    MAJOR = 0x06
    MINOR = 0x25
    DIRECTION = m.Direction.C2S

    target: m.ObjectId
    position: m.Vec3


@dataclass(kw_only=True)
class InputTileAction(m.Message):
    MAJOR = 0x06
    MINOR = 0x26
    DIRECTION = m.Direction.C2S

    area: m.ObjectId
    position: m.Vec3
    action: m.Int
