from dataclasses import dataclass

from .. import message as m
from ..types import ObjectType


@dataclass(kw_only=True)
class ObjListDeleteCreature(m.SubMessage):
    object_id: m.ObjectId
    instant_delete: m.Bool  # True = instant removal; False = play death animation first


@dataclass(kw_only=True)
class ObjListDeleteGeneric(m.SubMessage):
    object_id: m.ObjectId


@dataclass(kw_only=True)
class ObjListDeleteDoor(ObjListDeleteGeneric):
    pass


@dataclass(kw_only=True)
class ObjListDeletePlaceable(m.SubMessage):
    object_id: m.ObjectId
    instant_delete: m.Bool


@dataclass(kw_only=True)
class ObjListDeleteItem(m.SubMessage):
    object_id: m.ObjectId
    instant_delete: m.Bool


@dataclass(kw_only=True)
class ObjListDeleteTrigger(ObjListDeleteGeneric):
    pass


@dataclass(kw_only=True)
class ObjListDeleteAOE(ObjListDeleteGeneric):
    pass


# Canonical names for flat ObjList delete entries.
GameObjUpdateObjListDeleteCreature = ObjListDeleteCreature
GameObjUpdateObjListDeleteDoor = ObjListDeleteDoor
GameObjUpdateObjListDeletePlaceable = ObjListDeletePlaceable
GameObjUpdateObjListDeleteItem = ObjListDeleteItem
GameObjUpdateObjListDeleteTrigger = ObjListDeleteTrigger
GameObjUpdateObjListDeleteAOE = ObjListDeleteAOE


_GENERIC_DELETE_LUT: dict[ObjectType, type] = {
    ObjectType.DOOR: ObjListDeleteDoor,
    ObjectType.PLACEABLE: ObjListDeletePlaceable,
    ObjectType.ITEM: ObjListDeleteItem,
    ObjectType.TRIGGER: ObjListDeleteTrigger,
    ObjectType.AREAOFEFFECTOBJECT: ObjListDeleteAOE,
}
