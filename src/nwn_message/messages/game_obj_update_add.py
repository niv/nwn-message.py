from dataclasses import dataclass, field
from typing import Annotated

from .. import message as m
from ..net_types import VisualTransformData
from .game_obj_update_appearance import ItemAppearanceAndProps


@dataclass(kw_only=True)
class GameObjUpdateObjListAddCreature(m.SubMessage):
    object_id: m.ObjectId
    position: m.Vec3 = (0.0, 0.0, 0.0)
    orientation: m.Vec3 = (1.0, 0.0, 0.0)
    anim: m.Word = 0
    vt: VisualTransformData = field(default_factory=VisualTransformData)


@dataclass(kw_only=True)
class GameObjUpdateObjListAddDoor(m.SubMessage):
    object_id: m.ObjectId
    appearance_type: m.Dword
    generic_type: Annotated[m.Dword, m.IfEq("appearance_type", 0)]
    vt: VisualTransformData
    original_name: m.Bool
    loc_name: Annotated[m.LocStr, m.IfEq("original_name", True)]
    str_name: Annotated[m.String, m.IfEq("original_name", False)]
    trap_hostile: m.Bool
    anim: m.Word
    locked: m.Bool
    lockable: m.Bool
    plot: m.Bool
    clickable: m.Bool


@dataclass(kw_only=True)
class GameObjUpdateObjListAddAOE(m.SubMessage):
    object_id: m.ObjectId
    area_effect_id: m.Int
    target_oid: m.ObjectId


@dataclass(kw_only=True)
class GameObjUpdateObjListAddItem(m.SubMessage):
    object_id: m.ObjectId
    item: ItemAppearanceAndProps


@dataclass(kw_only=True)
class GameObjUpdateObjListAddTrigger(m.SubMessage):
    object_id: m.ObjectId
    name: m.LocStr
    is_trap: m.Bool
    is_area_transition: m.Bool
    cursor: m.Byte
    trap_hostile: Annotated[m.Bool, m.IfEq("is_trap", True)]
    trigger_height: m.Float
    vertices: Annotated[list[m.Vec3], m.SizePrefix.BYTE]


@dataclass(kw_only=True)
class GameObjUpdateObjListAddPlaceable(m.SubMessage):
    object_id: m.ObjectId
    original_name: m.Bool
    loc_name: Annotated[m.LocStr, m.IfEq("original_name", True)]
    str_name: Annotated[m.String, m.IfEq("original_name", False)]
    height: m.Byte
    hostile: m.Bool
    appearance: m.Word
    animation: m.Word
    is_body_bag: m.Bool
    body_bag_creature_id: Annotated[m.Dword, m.IfEq("is_body_bag", True)]
    plot: m.Bool
    useable: m.Bool
    disarmable: m.Bool
    lockable: m.Bool
    locked: m.Bool
    pickable: m.Bool
    description: m.Bool
    light_is_on: m.Bool
    vt: VisualTransformData
