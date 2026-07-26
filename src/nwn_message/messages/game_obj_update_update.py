import logging
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Annotated

from .. import message as m
from ..context import Context
from ..net_types import VisualTransformData
from ..types import ObjectType
from .game_obj_update_animation import AnimTypeData
from .game_obj_update_shared import (
    GameObjUpdateType,
    VisualEffectUpdate,
)

logger = logging.getLogger(__name__)

# pylint: disable=unused-argument


@dataclass(kw_only=True)
class PositionUpdate:
    x: Annotated[m.Float, m.QuantFloat(100.0, 16)]
    y: Annotated[m.Float, m.QuantFloat(100.0, 16)]
    z: Annotated[m.Float, m.RangeFloat(-20.0, 320.0, 18)]


OrientationUpdate2 = Annotated[
    m.Float | m.Vec3,
    m.Tagged(
        m.MessageType.BOOL,
        {
            False: m.Float,
            True: m.Vec3,
        },
    ),
]

OrientationUpdate2CreatureLockOn = Annotated[
    m.ObjectId,
    m.BoolPrefix(),
]

# class OrientationUpdate2CreatureLockOn:
#     # base: OrientationUpdate2
#     lock_on: bool
#     lock_target: Annotated[m.ObjectId, m.IfEq("lock_on", True)]


@dataclass(kw_only=True)
class OrientationUpdate:
    full: bool
    bearing: float | None = None  # QuantFloat(10.0, 12) when full=False
    ox: float | None = None  # RangeFloat(-2,2,16) when full=True
    oy: float | None = None
    oz: float | None = None

    # The creature update includes lock_on/lock_target after the direction;
    # the generic (non-creature) update does not.
    lock_on: bool = False
    lock_target: int | None = None  # ObjectId when lock_on=True

    @classmethod
    def read(
        cls, rd: m.Reader, context: Context, *, creature: bool = True
    ) -> "OrientationUpdate":
        full = rd.read_bool()
        if not full:
            bearing = rd.read_float()
            ox = oy = oz = None
        else:
            bearing = None
            ox = rd.read_float()
            oy = rd.read_float()
            oz = rd.read_float()
        lock_on = False
        lock_target = None
        if creature:
            lock_on = rd.read_bool()
            lock_target = rd.read_object_id() if lock_on else None
        return cls(
            full=full,
            bearing=bearing,
            ox=ox,
            oy=oy,
            oz=oz,
            lock_on=lock_on,
            lock_target=lock_target,
        )

    def write(self, wr: m.Writer, context: Context) -> None:
        wr.write_bool(self.full)
        if not self.full:
            wr.write_float(self.bearing)
        else:
            wr.write_float(self.ox)
            wr.write_float(self.oy)
            wr.write_float(self.oz)
        # lock_on/lock_target only written in creature context;
        # generic objects handle orientation inline in their own write().
        wr.write_bool(self.lock_on)
        if self.lock_on:
            wr.write_object_id(self.lock_target)


class MaterialShaderParamType(IntEnum):
    UNSET = 0
    INTEGER = 1
    VEC4 = 2


@dataclass(kw_only=True)
class MaterialShaderParam:
    material: m.ResRef
    param: m.ResRef
    type: Annotated[MaterialShaderParamType, m.MessageType.BYTE]
    int_val: Annotated[m.Int, m.IfEq("type", MaterialShaderParamType.INTEGER)]
    vec_val: Annotated[
        tuple[m.Float, m.Float, m.Float, m.Float],
        m.IfEq("type", MaterialShaderParamType.VEC4),
    ]


@dataclass(kw_only=True)
class CreatureClassEntry:
    class_id: m.Byte
    level: m.Byte
    school: Annotated[m.Byte, m.IfTwoDA("class_id", "classes", "PickSchool", {"1"})]
    domain1: Annotated[m.Byte, m.IfTwoDA("class_id", "classes", "PickDomains", {"1"})]
    domain2: Annotated[m.Byte, m.IfTwoDA("class_id", "classes", "PickDomains", {"1"})]


@dataclass(kw_only=True)
class PrimaryAttributes:
    race: m.Word
    subrace: m.String
    deity: m.String
    gender: m.Byte
    alignment_good_evil: m.Short
    alignment_law_chaos: m.Short
    selectable_when_dead: m.Bool
    lootable: m.Bool
    classes: Annotated[list[CreatureClassEntry], m.SizePrefix.BYTE]


@dataclass(kw_only=True)
class MasterAndAssociates:
    master_id: m.ObjectId
    associate_type: m.Word
    animal_companion: m.Bool
    familiar: m.Bool
    takes_commands: m.Bool


@dataclass(kw_only=True)
class NewPartyMemberName:
    # [TODO] surely this can be cleaned up
    original_name: bool
    first_name: m.LocStr | str  # LocStr when original; str otherwise
    last_name: m.LocStr | None  # LocStr when original; None otherwise

    @classmethod
    def read(cls, rd: m.Reader, context: Context) -> "NewPartyMemberName":
        original = rd.read_bool()
        if original:
            first = rd.read_locstr()
            last = rd.read_locstr()
        else:
            first = rd.read_str()
            last = None
        return cls(original_name=original, first_name=first, last_name=last)

    def write(self, wr: m.Writer, context: Context) -> None:
        wr.write_bool(self.original_name)
        if self.original_name:
            wr.write_locstr(self.first_name)
            wr.write_locstr(self.last_name)
        else:
            wr.write_str(str(self.first_name))


@dataclass(kw_only=True)
class PCPartyStatus:
    @dataclass(kw_only=True)
    class InvitedBy:
        inviter_id: m.Dword
        inviter_first: m.LocStr
        inviter_last: m.LocStr

    is_pc: m.Bool
    free_will: m.Bool
    in_party: m.Bool
    is_leader: m.Bool
    invited: m.Bool
    invited_by: Annotated[InvitedBy, m.IfEq("invited", True)]
    diseased: m.Bool
    poisoned: m.Bool


@dataclass(kw_only=True)
class GameObjUpdateObjListUpdate(m.SubMessage):
    pass


@dataclass(kw_only=True)
class CreatureWaypointUpdate:
    num_waypoints: int
    drive_mode: bool = False
    drive_mode_factor: float | None = None
    waypoints: list[tuple[float, float]] = field(default_factory=list)

    @classmethod
    def read(cls, rd: m.Reader, context: Context) -> "CreatureWaypointUpdate":
        num = rd.read_word()
        drive_mode = False
        drive_mode_factor = None
        if num > 0:
            drive_mode = rd.read_bool()
            if drive_mode:
                drive_mode_factor = rd.read_float()
        waypoints = [(rd.read_float(), rd.read_float()) for _ in range(num)]
        return cls(
            num_waypoints=num,
            drive_mode=drive_mode,
            drive_mode_factor=drive_mode_factor,
            waypoints=waypoints,
        )

    def write(self, wr: m.Writer, context: Context) -> None:
        wr.write_word(self.num_waypoints)
        if self.num_waypoints > 0:
            wr.write_bool(self.drive_mode)
            if self.drive_mode:
                wr.write_float(self.drive_mode_factor)
        for x, y in self.waypoints:
            wr.write_float(x)
            wr.write_float(y)


F = GameObjUpdateType  # alias for brevity


_PositionUpdate = tuple[
    Annotated[m.Float, m.QuantFloat(100.0, 16)],
    Annotated[m.Float, m.QuantFloat(100.0, 16)],
    Annotated[m.Float, m.RangeFloat(-20.0, 320.0, 18)],
]


@dataclass(kw_only=True)
class GameObjUpdateObjListUpdateCreature(GameObjUpdateObjListUpdate):
    object_id: m.ObjectId
    flags: Annotated[GameObjUpdateType, m.MessageType.DWORD]

    position: Annotated[_PositionUpdate, m.IfFlag("flags", F.OBJECT_POSITION_FLAG)]
    orientation: Annotated[
        OrientationUpdate, m.IfFlag("flags", F.OBJECT_ORIENTATION_FLAG)
    ]
    visual_transform: Annotated[
        VisualTransformData, m.IfFlag("flags", F.OBJECT_VISUAL_TRANSFORM_FLAG)
    ]
    shader_params: Annotated[
        list[MaterialShaderParam],
        m.SizePrefix.WORD,
        m.IfFlag("flags", F.OBJECT_MATERIAL_SHADER_PARAMETERS_FLAG),
    ]

    portrait_id: Annotated[m.Word, m.IfFlag("flags", F.OBJECT_PORTRAIT_FLAG)]
    custom_portrait: Annotated[
        m.ResRef,
        m.IfFlag("flags", F.OBJECT_PORTRAIT_FLAG),
        m.IfGt("portrait_id", 0xFFFD),
    ]

    hilite_r: Annotated[m.Float, m.IfFlag("flags", F.OBJECT_UI_FEEDBACK_FLAG)]
    hilite_g: Annotated[m.Float, m.IfFlag("flags", F.OBJECT_UI_FEEDBACK_FLAG)]
    hilite_b: Annotated[m.Float, m.IfFlag("flags", F.OBJECT_UI_FEEDBACK_FLAG)]
    cursor: Annotated[m.Word, m.IfFlag("flags", F.OBJECT_UI_FEEDBACK_FLAG)]

    useable: Annotated[m.Bool, m.IfFlag("flags", F.OBJECT_UI_FEEDBACK_FLAG)]
    discovery_mask: Annotated[m.Word, m.IfFlag("flags", F.OBJECT_UI_FEEDBACK_FLAG)]
    bubble_type: Annotated[m.Word, m.IfFlag("flags", F.OBJECT_UI_FEEDBACK_FLAG)]
    bubble_text: Annotated[m.String, m.IfFlag("flags", F.OBJECT_UI_FEEDBACK_FLAG)]

    textures: Annotated[
        list[tuple[m.ResRef, m.ResRef]],
        m.SizePrefix.DWORD,
        m.IfFlag("flags", F.OBJECT_TEXTURES_FLAG),
    ]

    anim_replacements: Annotated[
        list[tuple[m.ResRef, m.ResRef]],
        m.SizePrefix.DWORD,
        m.IfFlag("flags", F.OBJECT_ANIMATION_REPLACE_FLAG),
    ]

    anim_speed: Annotated[m.Float, m.IfFlag("flags", F.OBJECT_ANIMATION_FLAG)]
    anim_type_data: Annotated[AnimTypeData, m.IfFlag("flags", F.OBJECT_ANIMATION_FLAG)]

    effects: Annotated[
        list[VisualEffectUpdate],
        m.SizePrefix.WORD,
        m.IfFlag("flags", F.OBJECT_VISUAL_EFFECT_FLAG),
    ]

    client_path_number: Annotated[m.Byte, m.IfFlag("flags", F.OBJECT_ANIMATION_FLAG)]
    waypoints: Annotated[
        CreatureWaypointUpdate, m.IfFlag("flags", F.OBJECT_ANIMATION_FLAG)
    ]

    ai_state: Annotated[m.Word, m.IfFlag("flags", F.CREATURE_AISTATE_FLAG)]
    ai_action: Annotated[m.Byte, m.IfFlag("flags", F.CREATURE_AISTATE_FLAG)]
    ai_activities: Annotated[m.Word, m.IfFlag("flags", F.CREATURE_AISTATE_FLAG)]
    ai_reaction: Annotated[m.Byte, m.IfFlag("flags", F.CREATURE_AISTATE_FLAG)]
    in_combat: Annotated[m.Bool, m.IfFlag("flags", F.CREATURE_AISTATE_FLAG)]
    combat_target_id: Annotated[
        m.ObjectId, m.IfFlag("flags", F.CREATURE_AISTATE_FLAG), m.IfEq("ai_action", 2)
    ]

    walk_rate: Annotated[m.Float, m.IfFlag("flags", F.CREATURE_MOVE_RATE_FLAG)]
    run_rate: Annotated[m.Float, m.IfFlag("flags", F.CREATURE_MOVE_RATE_FLAG)]

    area_id: Annotated[m.ObjectId, m.IfFlag("flags", F.CREATURE_PARTYMEMBER_AREA_FLAG)]

    party_x: Annotated[
        m.Int, m.IfFlag("flags", F.CREATURE_PARTYMEMBER_POSITION_FLAG), m.Bits(10)
    ]
    party_y: Annotated[
        m.Int, m.IfFlag("flags", F.CREATURE_PARTYMEMBER_POSITION_FLAG), m.Bits(10)
    ]

    hp_current: Annotated[m.Short, m.IfFlag("flags", F.CREATURE_HIT_POINTS_FLAG)]
    hp_base: Annotated[m.Short, m.IfFlag("flags", F.CREATURE_HIT_POINTS_FLAG)]
    hp_temp: Annotated[m.Short, m.IfFlag("flags", F.CREATURE_HIT_POINTS_FLAG)]
    hp_max: Annotated[m.Short, m.IfFlag("flags", F.CREATURE_HIT_POINTS_FLAG)]

    party_member_name: Annotated[
        NewPartyMemberName, m.IfFlag("flags", F.CREATURE_NEWPARTYMEMBER_FLAG)
    ]

    pc_party_status: Annotated[
        PCPartyStatus, m.IfFlag("flags", F.CREATURE_PC_PARTY_STATUS_FLAG)
    ]

    heard: Annotated[m.Bool, m.IfFlag("flags", F.CREATURE_PERCEPTION_TO_PLAYER_FLAG)]
    seen: Annotated[m.Bool, m.IfFlag("flags", F.CREATURE_PERCEPTION_TO_PLAYER_FLAG)]
    invisible: Annotated[
        m.Bool, m.IfFlag("flags", F.CREATURE_PERCEPTION_TO_PLAYER_FLAG)
    ]

    associate_state: Annotated[
        m.Word, m.IfFlag("flags", F.CREATURE_ASSOCIATE_STATE_FLAG)
    ]

    damage_level: Annotated[m.Byte, m.IfFlag("flags", F.CREATURE_DAMAGE_LEVEL_FLAG)]

    primary_attributes: Annotated[
        PrimaryAttributes, m.IfFlag("flags", F.CREATURE_PRIMARY_ATTRIBUTES_FLAG)
    ]

    master_and_assoc: Annotated[
        MasterAndAssociates, m.IfFlag("flags", F.CREATURE_MASTER_AND_ASSOCIATES_FLAG)
    ]


@dataclass(kw_only=True)
class GameObjUpdateObjListUpdateGeneric(GameObjUpdateObjListUpdate):
    object_type: ObjectType
    object_id: int
    flags: int

    position: m.Vec3 | None = None
    orientation: OrientationUpdate | None = None
    visual_transform: VisualTransformData | None = None
    shader_params: list[MaterialShaderParam] | None = None
    portrait_id: int | None = None
    custom_portrait: str | None = None

    # UI_FEEDBACK_FLAG
    hilite_r: float | None = None
    hilite_g: float | None = None
    hilite_b: float | None = None
    cursor: int | None = None
    useable: bool | None = None
    discovery_mask: int | None = None
    bubble_type: int | None = None
    bubble_text: str | None = None

    textures: list[tuple[str, str]] | None = None
    anim_replacements: list[tuple[str, str]] | None = None
    anim_speed: float | None = None
    animation: int | None = None  # WORD — simple animation id
    effects: list[VisualEffectUpdate] | None = None

    # Door / Placeable: TRAPS_AND_LOCKS
    trap_hostile: bool | None = None
    trapped: bool | None = None
    locked: bool | None = None
    lockable: bool | None = None
    recoverable: bool | None = None
    clickable: bool | None = None  # door only (IsAreaTransition)

    # Door / Placeable / Item: NAME
    name: m.LocStr | str | None = None

    # Item: ITEM_HIDDEN
    hidden: bool | None = None

    @classmethod
    def read(
        cls, rd: m.Reader, context: Context, object_type: ObjectType
    ) -> "GameObjUpdateObjListUpdateGeneric":
        object_id = rd.read_object_id()
        flags = rd.read_dword()
        context.fields["flags"] = flags
        data: dict = {
            "object_type": object_type,
            "object_id": object_id,
            "flags": flags,
        }

        if flags & F.OBJECT_POSITION_FLAG:
            data["position"] = (rd.read_float(), rd.read_float(), rd.read_float())

        if flags & F.OBJECT_ORIENTATION_FLAG:
            # Generic objects do NOT have lock_on/lock_target (creature-only).
            data["orientation"] = OrientationUpdate.read(rd, context, creature=False)

        if flags & F.OBJECT_VISUAL_TRANSFORM_FLAG:
            data["visual_transform"] = m.read_dataclass(
                VisualTransformData, rd, context
            )

        if flags & F.OBJECT_MATERIAL_SHADER_PARAMETERS_FLAG:
            count = rd.read_word()
            data["shader_params"] = [
                m.read_dataclass(MaterialShaderParam, rd, context) for _ in range(count)
            ]

        if flags & F.OBJECT_PORTRAIT_FLAG:
            pid = rd.read_word()
            data["portrait_id"] = pid
            if pid >= 0xFFFE:
                data["custom_portrait"] = rd.read_resref()

        if flags & F.OBJECT_UI_FEEDBACK_FLAG:
            data["hilite_r"] = rd.read_float()
            data["hilite_g"] = rd.read_float()
            data["hilite_b"] = rd.read_float()
            data["cursor"] = rd.read_int()
            data["useable"] = rd.read_bool()
            data["discovery_mask"] = rd.read_int()
            data["bubble_type"] = rd.read_int()
            data["bubble_text"] = rd.read_str()

        if flags & F.OBJECT_TEXTURES_FLAG:
            n = rd.read_dword()
            data["textures"] = [(rd.read_resref(), rd.read_resref()) for _ in range(n)]

        if flags & F.OBJECT_ANIMATION_REPLACE_FLAG:
            n = rd.read_dword()
            data["anim_replacements"] = [
                (rd.read_resref(), rd.read_resref()) for _ in range(n)
            ]

        if flags & F.OBJECT_ANIMATION_FLAG:
            data["anim_speed"] = rd.read_float()

        if flags & F.OBJECT_ANIMATION_FLAG:
            data["animation"] = rd.read_word()

        # VISUAL_EFFECT_FLAG
        if flags & F.OBJECT_VISUAL_EFFECT_FLAG:
            n_eff = rd.read_word()
            data["effects"] = [
                m.read_dataclass(VisualEffectUpdate, rd, context) for _ in range(n_eff)
            ]

        _read_type_specific(object_type, flags, rd, context, data)

        return cls(**data)

    def write(self, wr: m.Writer, context: Context) -> None:
        flags = self.flags

        wr.write_object_id(self.object_id)
        wr.write_dword(flags)

        if flags & F.OBJECT_POSITION_FLAG:
            assert self.position is not None
            wr.write_float(self.position[0])
            wr.write_float(self.position[1])
            wr.write_float(self.position[2])

        if flags & F.OBJECT_ORIENTATION_FLAG:
            assert self.orientation is not None
            wr.write_bool(self.orientation.full)
            if not self.orientation.full:
                wr.write_float(self.orientation.bearing)
            else:
                wr.write_float(self.orientation.ox)
                wr.write_float(self.orientation.oy)
                wr.write_float(self.orientation.oz)

        if flags & F.OBJECT_VISUAL_TRANSFORM_FLAG:
            m.write_dataclass(self.visual_transform, wr, context)

        if flags & F.OBJECT_MATERIAL_SHADER_PARAMETERS_FLAG:
            params = self.shader_params or []
            wr.write_word(len(params))
            for p in params:
                wr.write_resref(p.material)
                wr.write_resref(p.param)
                wr.write_byte(int(p.type))
                if p.type == MaterialShaderParamType.INTEGER:
                    wr.write_int(p.int_val)
                elif p.type == MaterialShaderParamType.VEC4:
                    v0, v1, v2, v3 = p.vec_val
                    wr.write_float(v0)
                    wr.write_float(v1)
                    wr.write_float(v2)
                    wr.write_float(v3)

        if flags & F.OBJECT_PORTRAIT_FLAG:
            wr.write_word(self.portrait_id)
            if self.portrait_id >= 0xFFFE:
                wr.write_resref(self.custom_portrait)

        if flags & F.OBJECT_UI_FEEDBACK_FLAG:
            wr.write_float(self.hilite_r)
            wr.write_float(self.hilite_g)
            wr.write_float(self.hilite_b)
            wr.write_int(self.cursor)
            wr.write_bool(self.useable)
            wr.write_int(self.discovery_mask)
            wr.write_int(self.bubble_type)
            wr.write_str(self.bubble_text)

        if flags & F.OBJECT_TEXTURES_FLAG:
            textures = self.textures or []
            wr.write_dword(len(textures))
            for old_name, new_name in textures:
                wr.write_resref(old_name)
                wr.write_resref(new_name)

        if flags & F.OBJECT_ANIMATION_REPLACE_FLAG:
            replacements = self.anim_replacements or []
            wr.write_dword(len(replacements))
            for old_name, new_name in replacements:
                wr.write_resref(old_name)
                wr.write_resref(new_name)

        if flags & F.OBJECT_ANIMATION_FLAG:
            wr.write_float(self.anim_speed)
            wr.write_word(self.animation)

        if flags & F.OBJECT_VISUAL_EFFECT_FLAG:
            effects = self.effects or []
            wr.write_word(len(effects))
            for effect in effects:
                m.write_dataclass(effect, wr, context)

        _write_type_specific(self.object_type, flags, wr, self)


@dataclass(kw_only=True)
class ObjListUpdateDoor(GameObjUpdateObjListUpdateGeneric):
    pass


@dataclass(kw_only=True)
class ObjListUpdatePlaceable(GameObjUpdateObjListUpdateGeneric):
    pass


@dataclass(kw_only=True)
class ObjListUpdateItem(GameObjUpdateObjListUpdateGeneric):
    pass


@dataclass(kw_only=True)
class ObjListUpdateTrigger(GameObjUpdateObjListUpdateGeneric):
    pass


@dataclass(kw_only=True)
class ObjListUpdateAOE(GameObjUpdateObjListUpdateGeneric):
    pass


# Canonical names for flat ObjList update entries.
GameObjUpdateObjListUpdateDoor = ObjListUpdateDoor
GameObjUpdateObjListUpdatePlaceable = ObjListUpdatePlaceable
GameObjUpdateObjListUpdateItem = ObjListUpdateItem
GameObjUpdateObjListUpdateTrigger = ObjListUpdateTrigger
GameObjUpdateObjListUpdateAOE = ObjListUpdateAOE


_GENERIC_UPDATE_LUT: dict[ObjectType, type[GameObjUpdateObjListUpdateGeneric]] = {
    ObjectType.DOOR: ObjListUpdateDoor,
    ObjectType.PLACEABLE: ObjListUpdatePlaceable,
    ObjectType.ITEM: ObjListUpdateItem,
    ObjectType.TRIGGER: ObjListUpdateTrigger,
    ObjectType.AREAOFEFFECTOBJECT: ObjListUpdateAOE,
}


def _read_type_specific(
    object_type: ObjectType,
    flags: int,
    rd: m.Reader,
    context: Context,
    data: dict,
) -> None:
    if object_type in (ObjectType.DOOR, ObjectType.PLACEABLE):
        # Door and Placeable share the same TRAPS_AND_LOCKS + NAME layout.
        if flags & F.OBJECT_TRAPS_AND_LOCKS_FLAG:
            data["trap_hostile"] = rd.read_bool()
            data["trapped"] = rd.read_bool()
            data["locked"] = rd.read_bool()
            data["lockable"] = rd.read_bool()
            data["recoverable"] = rd.read_bool()
            if object_type == ObjectType.DOOR:
                data["clickable"] = rd.read_bool()

        if flags & F.OBJECT_NAME_FLAG:
            original = rd.read_bool()
            if original:
                data["name"] = rd.read_locstr()
            else:
                data["name"] = rd.read_str()

    elif object_type == ObjectType.TRIGGER:
        if flags & F.OBJECT_TRAPS_AND_LOCKS_FLAG:
            object_id = data["object_id"]
            is_trap = context.hack_get_is_trap(object_id)
            if is_trap:
                data["trap_hostile"] = rd.read_bool()
                data["recoverable"] = rd.read_bool()
            else:
                data["clickable"] = rd.read_bool()

    elif object_type == ObjectType.ITEM:
        if flags & F.OBJECT_NAME_FLAG:
            original = rd.read_bool()
            if original:
                data["name"] = rd.read_locstr()
            else:
                data["name"] = rd.read_str()

        # UPDATE_ITEM_HIDDEN_FLAG = 0x40 (same bit as CREATURE_AISTATE_FLAG)
        if flags & 0x00000040:
            data["hidden"] = rd.read_bool()

    # AREAOFEFFECTOBJECT has no type-specific update data.


def _write_type_specific(
    object_type: ObjectType,
    flags: int,
    wr: m.Writer,
    obj: GameObjUpdateObjListUpdateGeneric,
) -> None:
    if object_type in (ObjectType.DOOR, ObjectType.PLACEABLE):
        if flags & F.OBJECT_TRAPS_AND_LOCKS_FLAG:
            wr.write_bool(obj.trap_hostile)
            wr.write_bool(obj.trapped)
            wr.write_bool(obj.locked)
            wr.write_bool(obj.lockable)
            wr.write_bool(obj.recoverable)
            if object_type == ObjectType.DOOR:
                wr.write_bool(obj.clickable)

        if flags & F.OBJECT_NAME_FLAG:
            name = obj.name
            if isinstance(name, m.LocStr):
                wr.write_bool(True)
                wr.write_locstr(name)
            else:
                wr.write_bool(False)
                wr.write_str(name)

    elif object_type == ObjectType.TRIGGER:
        if flags & F.OBJECT_TRAPS_AND_LOCKS_FLAG:
            if obj.clickable is None:
                wr.write_bool(obj.trap_hostile)
                wr.write_bool(obj.recoverable)
            else:
                wr.write_bool(obj.clickable)

    elif object_type == ObjectType.ITEM:
        if flags & F.OBJECT_NAME_FLAG:
            name = obj.name
            if isinstance(name, m.LocStr):
                wr.write_bool(True)
                wr.write_locstr(name)
            else:
                wr.write_bool(False)
                wr.write_str(name)

        if flags & 0x00000040:
            wr.write_bool(obj.hidden)
