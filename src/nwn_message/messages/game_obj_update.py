import logging
from dataclasses import dataclass
from typing import Self, cast

from .. import message as m
from ..context import Context
from ..net_types import VisualTransformData
from .game_obj_update_add import *
from .game_obj_update_appearance import *
from .game_obj_update_delete import *
from .game_obj_update_gui import *
from .game_obj_update_playerinfo import *

# pylint: disable=wildcard-import, unused-wildcard-import
from .game_obj_update_shared import *
from .game_obj_update_update import *
from .game_obj_update_update import _GENERIC_UPDATE_LUT

logger = logging.getLogger(__name__)

INVALID_OBJECT_ID = 0x7F000000
VISUAL_EFFECT_COW = 999


@dataclass(kw_only=True)
class ObjListWorkRemaining(m.SubMessage):
    stages_done: m.Byte
    stages_total: m.Byte


ObjListAddEntry = (
    GameObjUpdateObjListAddCreature
    | GameObjUpdateObjListAddDoor
    | GameObjUpdateObjListAddAOE
    | GameObjUpdateObjListAddItem
    | GameObjUpdateObjListAddTrigger
    | GameObjUpdateObjListAddPlaceable
)

ObjListUpdateEntry = (
    GameObjUpdateObjListUpdateCreature
    | GameObjUpdateObjListUpdateDoor
    | GameObjUpdateObjListUpdatePlaceable
    | GameObjUpdateObjListUpdateItem
    | GameObjUpdateObjListUpdateTrigger
    | GameObjUpdateObjListUpdateAOE
)

ObjListDeleteEntry = (
    GameObjUpdateObjListDeleteCreature
    | GameObjUpdateObjListDeleteDoor
    | GameObjUpdateObjListDeletePlaceable
    | GameObjUpdateObjListDeleteItem
    | GameObjUpdateObjListDeleteTrigger
    | GameObjUpdateObjListDeleteAOE
)

ObjListGuiEntry = (
    GameObjUpdateObjListGuiInventoryAdd
    | GameObjUpdateObjListGuiInventoryDelete
    | GameObjUpdateObjListGuiInventoryUpdate
    | GameObjUpdateObjListGuiRepositoryAdd
    | GameObjUpdateObjListGuiRepositoryDelete
    | GameObjUpdateObjListGuiRepositoryUpdate
    | GameObjUpdateObjListGuiRepositoryMove
    | GameObjUpdateObjListGuiContainerPages
    | GameObjUpdateObjListGuiContainerAdd
    | GameObjUpdateObjListGuiContainerDelete
    | GameObjUpdateObjListGuiContainerUpdate
    | GameObjUpdateObjListGuiContainerMove
    | GameObjUpdateObjListGuiStorePages
    | GameObjUpdateObjListGuiStoreAdd
    | GameObjUpdateObjListGuiStoreDelete
    | GameObjUpdateObjListGuiStoreReposition
    | GameObjUpdateObjListGuiCharacterSheet
    | GameObjUpdateObjListGuiQuickbarUseCount
)

ObjListEntry = (
    ObjListAddEntry
    | ObjListUpdateEntry
    | ObjListDeleteEntry
    | GameObjUpdateObjListAppearanceCreature
    | GameObjUpdateObjListPlayerInfo
    | ObjListWorkRemaining
    | ObjListGuiEntry
)

_ADD_OBJECT_TYPE_BY_CLS: dict[type, ObjectType] = {
    GameObjUpdateObjListAddCreature: ObjectType.CREATURE,
    GameObjUpdateObjListAddDoor: ObjectType.DOOR,
    GameObjUpdateObjListAddPlaceable: ObjectType.PLACEABLE,
    GameObjUpdateObjListAddItem: ObjectType.ITEM,
    GameObjUpdateObjListAddTrigger: ObjectType.TRIGGER,
    GameObjUpdateObjListAddAOE: ObjectType.AREAOFEFFECTOBJECT,
}

_ADD_CLS_BY_OBJECT_TYPE: dict[ObjectType, type] = {
    v: k for k, v in _ADD_OBJECT_TYPE_BY_CLS.items()
}

_UPDATE_OBJECT_TYPE_BY_CLS: dict[type, ObjectType] = {
    GameObjUpdateObjListUpdateCreature: ObjectType.CREATURE,
    GameObjUpdateObjListUpdateDoor: ObjectType.DOOR,
    GameObjUpdateObjListUpdatePlaceable: ObjectType.PLACEABLE,
    GameObjUpdateObjListUpdateItem: ObjectType.ITEM,
    GameObjUpdateObjListUpdateTrigger: ObjectType.TRIGGER,
    GameObjUpdateObjListUpdateAOE: ObjectType.AREAOFEFFECTOBJECT,
}

_DELETE_OBJECT_TYPE_BY_CLS: dict[type, ObjectType] = {
    GameObjUpdateObjListDeleteCreature: ObjectType.CREATURE,
    GameObjUpdateObjListDeleteDoor: ObjectType.DOOR,
    GameObjUpdateObjListDeletePlaceable: ObjectType.PLACEABLE,
    GameObjUpdateObjListDeleteItem: ObjectType.ITEM,
    GameObjUpdateObjListDeleteTrigger: ObjectType.TRIGGER,
    GameObjUpdateObjListDeleteAOE: ObjectType.AREAOFEFFECTOBJECT,
}

_DELETE_CLS_BY_OBJECT_TYPE: dict[ObjectType, type] = {
    v: k for k, v in _DELETE_OBJECT_TYPE_BY_CLS.items()
}

_ADD_ENTRY_TYPES = tuple(_ADD_OBJECT_TYPE_BY_CLS.keys())
_UPDATE_ENTRY_TYPES = tuple(_UPDATE_OBJECT_TYPE_BY_CLS.keys())
_DELETE_ENTRY_TYPES = tuple(_DELETE_OBJECT_TYPE_BY_CLS.keys())
_GUI_ENTRY_TYPES = (
    GameObjUpdateObjListGuiInventoryAdd,
    GameObjUpdateObjListGuiInventoryDelete,
    GameObjUpdateObjListGuiInventoryUpdate,
    GameObjUpdateObjListGuiRepositoryAdd,
    GameObjUpdateObjListGuiRepositoryDelete,
    GameObjUpdateObjListGuiRepositoryUpdate,
    GameObjUpdateObjListGuiRepositoryMove,
    GameObjUpdateObjListGuiContainerPages,
    GameObjUpdateObjListGuiContainerAdd,
    GameObjUpdateObjListGuiContainerDelete,
    GameObjUpdateObjListGuiContainerUpdate,
    GameObjUpdateObjListGuiContainerMove,
    GameObjUpdateObjListGuiStorePages,
    GameObjUpdateObjListGuiStoreAdd,
    GameObjUpdateObjListGuiStoreDelete,
    GameObjUpdateObjListGuiStoreReposition,
    GameObjUpdateObjListGuiCharacterSheet,
    GameObjUpdateObjListGuiQuickbarUseCount,
)

_GUI_INVENTORY_READ_OP: dict[int, type] = {
    ord("A"): GameObjUpdateObjListGuiInventoryAdd,
    ord("D"): GameObjUpdateObjListGuiInventoryDelete,
    ord("U"): GameObjUpdateObjListGuiInventoryUpdate,
}

_GUI_REPOSITORY_READ_OP: dict[int, type] = {
    ord("A"): GameObjUpdateObjListGuiRepositoryAdd,
    ord("D"): GameObjUpdateObjListGuiRepositoryDelete,
    ord("U"): GameObjUpdateObjListGuiRepositoryUpdate,
    ord("M"): GameObjUpdateObjListGuiRepositoryMove,
}

_GUI_CONTAINER_READ_OP: dict[int, type] = {
    ord("P"): GameObjUpdateObjListGuiContainerPages,
    ord("A"): GameObjUpdateObjListGuiContainerAdd,
    ord("D"): GameObjUpdateObjListGuiContainerDelete,
    ord("U"): GameObjUpdateObjListGuiContainerUpdate,
    ord("M"): GameObjUpdateObjListGuiContainerMove,
}

_GUI_STORE_READ_OP: dict[int, type] = {
    ord("P"): GameObjUpdateObjListGuiStorePages,
    ord("A"): GameObjUpdateObjListGuiStoreAdd,
    ord("D"): GameObjUpdateObjListGuiStoreDelete,
    ord("U"): GameObjUpdateObjListGuiStoreReposition,
}

_GUI_INVENTORY_WRITE_OP: dict[type, int] = {
    GameObjUpdateObjListGuiInventoryAdd: ord("A"),
    GameObjUpdateObjListGuiInventoryDelete: ord("D"),
    GameObjUpdateObjListGuiInventoryUpdate: ord("U"),
}

_GUI_REPOSITORY_WRITE_OP: dict[type, int] = {
    GameObjUpdateObjListGuiRepositoryAdd: ord("A"),
    GameObjUpdateObjListGuiRepositoryDelete: ord("D"),
    GameObjUpdateObjListGuiRepositoryUpdate: ord("U"),
    GameObjUpdateObjListGuiRepositoryMove: ord("M"),
}

_GUI_CONTAINER_WRITE_OP: dict[type, int] = {
    GameObjUpdateObjListGuiContainerPages: ord("P"),
    GameObjUpdateObjListGuiContainerAdd: ord("A"),
    GameObjUpdateObjListGuiContainerDelete: ord("D"),
    GameObjUpdateObjListGuiContainerUpdate: ord("U"),
    GameObjUpdateObjListGuiContainerMove: ord("M"),
}

_GUI_STORE_WRITE_OP: dict[type, int] = {
    GameObjUpdateObjListGuiStorePages: ord("P"),
    GameObjUpdateObjListGuiStoreAdd: ord("A"),
    GameObjUpdateObjListGuiStoreDelete: ord("D"),
    GameObjUpdateObjListGuiStoreReposition: ord("U"),
}


def _read_objlist_add(rd: m.Reader, context: Context) -> ObjListAddEntry:
    object_type = ObjectType(rd.read_byte())
    concrete_cls = _ADD_CLS_BY_OBJECT_TYPE.get(object_type)
    if concrete_cls is None:
        raise NotImplementedError(f"Unsupported Add ObjectType: {object_type}")
    dc = m.read_dataclass(concrete_cls, rd, context)
    if isinstance(dc, GameObjUpdateObjListAddTrigger):
        context.hack_set_is_trap(dc.object_id, dc.is_trap)
    return dc


def _read_objlist_update(rd: m.Reader, context: Context) -> ObjListUpdateEntry:
    object_type = ObjectType(rd.read_byte())
    if object_type == ObjectType.CREATURE:
        return m.read_dataclass(GameObjUpdateObjListUpdateCreature, rd, context)

    concrete_cls = _GENERIC_UPDATE_LUT.get(object_type)
    if concrete_cls is None:
        raise NotImplementedError(f"Unsupported Update ObjectType: {object_type}")
    return GameObjUpdateObjListUpdateGeneric.read.__func__(
        concrete_cls, rd, context, object_type=object_type
    )


def _read_objlist_delete(rd: m.Reader, context: Context) -> ObjListDeleteEntry:
    object_type = ObjectType(rd.read_byte())
    concrete_cls = _DELETE_CLS_BY_OBJECT_TYPE.get(object_type)
    if concrete_cls is None:
        raise NotImplementedError(f"Unsupported Delete ObjectType: {object_type}")
    return m.read_dataclass(concrete_cls, rd, context)


def _write_objlist_add(wr: m.Writer, context: Context, entry: ObjListAddEntry) -> None:
    object_type = _ADD_OBJECT_TYPE_BY_CLS.get(type(entry))
    if object_type is None:
        raise NotImplementedError(
            f"Unsupported Add entry class: {type(entry).__name__}"
        )
    wr.write_byte(int(object_type))
    m.write_dataclass(entry, wr, context)


def _write_objlist_update(
    wr: m.Writer, context: Context, entry: ObjListUpdateEntry
) -> None:
    object_type = _UPDATE_OBJECT_TYPE_BY_CLS.get(type(entry))
    if object_type is None:
        raise NotImplementedError(
            f"Unsupported Update entry class: {type(entry).__name__}"
        )
    wr.write_byte(int(object_type))
    m.write_dataclass(entry, wr, context)


def _write_objlist_delete(
    wr: m.Writer, context: Context, entry: ObjListDeleteEntry
) -> None:
    object_type = _DELETE_OBJECT_TYPE_BY_CLS.get(type(entry))
    if object_type is None:
        raise NotImplementedError(
            f"Unsupported Delete entry class: {type(entry).__name__}"
        )
    wr.write_byte(int(object_type))
    m.write_dataclass(entry, wr, context)


def _read_objlist_gui(rd: m.Reader, context: Context) -> ObjListGuiEntry:
    element_type = rd.read_char()
    if element_type in (ord("I"), ord("i")):
        op_type = rd.read_char()
        concrete_cls = _GUI_INVENTORY_READ_OP.get(op_type)
        if concrete_cls is None:
            raise NotImplementedError(
                f"Unsupported GUI inventory op: {chr(op_type)!r} ({op_type})"
            )
        return m.read_dataclass(concrete_cls, rd, context)

    if element_type in (ord("R"), ord("r"), ord("B"), ord("A")):
        op_type = rd.read_char()
        concrete_cls = _GUI_REPOSITORY_READ_OP.get(op_type)
        if concrete_cls is None:
            raise NotImplementedError(
                f"Unsupported GUI repository op: {chr(op_type)!r} ({op_type})"
            )
        return m.read_dataclass(concrete_cls, rd, context)

    if element_type in (ord("C"), ord("c")):
        op_type = rd.read_char()
        concrete_cls = _GUI_CONTAINER_READ_OP.get(op_type)
        if concrete_cls is None:
            raise NotImplementedError(
                f"Unsupported GUI container op: {chr(op_type)!r} ({op_type})"
            )
        return m.read_dataclass(concrete_cls, rd, context)

    if element_type == ord("M"):
        op_type = rd.read_char()
        concrete_cls = _GUI_STORE_READ_OP.get(op_type)
        if concrete_cls is None:
            raise NotImplementedError(
                f"Unsupported GUI store op: {chr(op_type)!r} ({op_type})"
            )
        return m.read_dataclass(concrete_cls, rd, context)

    if element_type == ord("S"):
        return m.read_dataclass(GameObjUpdateObjListGuiCharacterSheet, rd, context)

    if element_type == ord("Q"):
        return m.read_dataclass(GameObjUpdateObjListGuiQuickbarUseCount, rd, context)

    raise NotImplementedError(
        f"Unsupported GUI element type: {chr(element_type)!r} ({element_type})"
    )


def _write_objlist_gui(wr: m.Writer, context: Context, entry: ObjListGuiEntry) -> None:
    entry_cls = type(entry)

    op_type = _GUI_INVENTORY_WRITE_OP.get(entry_cls)
    if op_type is not None:
        wr.write_char(ord("I"))
        wr.write_char(op_type)
        m.write_dataclass(entry, wr, context)
        return

    op_type = _GUI_REPOSITORY_WRITE_OP.get(entry_cls)
    if op_type is not None:
        wr.write_char(ord("R"))
        wr.write_char(op_type)
        m.write_dataclass(entry, wr, context)
        return

    op_type = _GUI_CONTAINER_WRITE_OP.get(entry_cls)
    if op_type is not None:
        wr.write_char(ord("C"))
        wr.write_char(op_type)
        m.write_dataclass(entry, wr, context)
        return

    op_type = _GUI_STORE_WRITE_OP.get(entry_cls)
    if op_type is not None:
        wr.write_char(ord("M"))
        wr.write_char(op_type)
        m.write_dataclass(entry, wr, context)
        return

    if isinstance(entry, GameObjUpdateObjListGuiCharacterSheet):
        wr.write_char(ord("S"))
        m.write_dataclass(entry, wr, context)
        return

    if isinstance(entry, GameObjUpdateObjListGuiQuickbarUseCount):
        wr.write_char(ord("Q"))
        m.write_dataclass(entry, wr, context)
        return

    raise NotImplementedError(f"Unsupported GUI entry class: {type(entry).__name__}")


@dataclass(kw_only=True)
class GameObjUpdateObjList(m.Message):
    MAJOR = 0x05
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    entries: list[ObjListEntry]

    @classmethod
    def read(cls, rd: m.Reader, context: Context) -> Self:
        entries = []
        while rd.more():
            entry_type = rd.read_char()
            if entry_type == ord("A"):
                entry = _read_objlist_add(rd, context)
            elif entry_type == ord("U"):
                entry = _read_objlist_update(rd, context)
            elif entry_type == ord("D"):
                entry = _read_objlist_delete(rd, context)
            elif entry_type == ord("P"):
                entry = m.read_dataclass(
                    GameObjUpdateObjListAppearanceCreature, rd, context
                )
            elif entry_type == ord("I"):
                entry = m.read_dataclass(GameObjUpdateObjListPlayerInfo, rd, context)
            elif entry_type == ord("W"):
                entry = m.read_dataclass(ObjListWorkRemaining, rd, context)
            elif entry_type == ord("G"):
                entry = _read_objlist_gui(rd, context)
            else:
                raise NotImplementedError(
                    f"Unknown ObjList entry type: {chr(entry_type)!r} ({entry_type})"
                )
            entries.append(entry)
        return cls(entries=entries)

    def iter_submessages(self) -> tuple:
        return tuple(self.entries)

    def write(self, wr: m.Writer, context: Context) -> None:
        for entry in self.entries:
            if isinstance(entry, _ADD_ENTRY_TYPES):
                wr.write_char(ord("A"))
                _write_objlist_add(wr, context, cast(ObjListAddEntry, entry))
            elif isinstance(entry, _UPDATE_ENTRY_TYPES):
                wr.write_char(ord("U"))
                _write_objlist_update(wr, context, cast(ObjListUpdateEntry, entry))
            elif isinstance(entry, _DELETE_ENTRY_TYPES):
                wr.write_char(ord("D"))
                _write_objlist_delete(wr, context, cast(ObjListDeleteEntry, entry))
            elif isinstance(entry, GameObjUpdateObjListAppearanceCreature):
                wr.write_char(ord("P"))
                m.write_dataclass(entry, wr, context)
            elif isinstance(entry, GameObjUpdateObjListPlayerInfo):
                wr.write_char(ord("I"))
                m.write_dataclass(entry, wr, context)
            elif isinstance(entry, ObjListWorkRemaining):
                wr.write_char(ord("W"))
                m.write_dataclass(entry, wr, context)
            elif isinstance(entry, _GUI_ENTRY_TYPES):
                wr.write_char(ord("G"))
                _write_objlist_gui(wr, context, entry)
            else:
                raise NotImplementedError(
                    f"Unsupported ObjList entry class: {type(entry).__name__}"
                )


@dataclass(kw_only=True)
class GameObjUpdateObjControl(m.Message):
    MAJOR = 0x05
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    player_id: m.Dword
    object_id: m.ObjectId


def _vis_effect_uses_source(effect_id: int, context: Context) -> bool:
    if effect_id == VISUAL_EFFECT_COW:
        return True
    try:
        vis_type = context.twoda("visualeffects", effect_id, "Type_FD")
    except IndexError, KeyError:
        return False
    return vis_type in {"P", "B"}


@dataclass(kw_only=True)
class GameObjUpdateVisEffect(m.Message):
    MAJOR = 0x05
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    target_id: m.ObjectId
    visual_effect_id: m.Word
    target_location: m.Vec3
    source_id: m.ObjectId = INVALID_OBJECT_ID
    source_node: m.Byte = 0
    target_node: m.Byte = 0
    source_location: m.Vec3 = (0.0, 0.0, 0.0)
    duration: m.Float = 0.0
    vt: VisualTransformData | None = None

    @classmethod
    def read(cls, rd: m.Reader, context: Context) -> Self:
        target_id = rd.read_object_id()
        visual_effect_id = rd.read_word()
        target_x = rd.read_float()
        target_y = rd.read_float()
        target_z = rd.read_float()

        source_id = INVALID_OBJECT_ID
        source_node = 0
        target_node = 0
        source_x = 0.0
        source_y = 0.0
        source_z = 0.0
        duration = 0.0

        if _vis_effect_uses_source(visual_effect_id, context):
            source_id = rd.read_object_id()
            source_node = rd.read_byte()
            target_node = rd.read_byte()
            source_x = rd.read_float()
            source_y = rd.read_float()
            source_z = rd.read_float()
            if target_id == INVALID_OBJECT_ID:
                duration = rd.read_float()

        vt = m.read_dataclass(VisualTransformData, rd, context)

        return cls(
            target_id=target_id,
            visual_effect_id=visual_effect_id,
            target_location=(target_x, target_y, target_z),
            source_id=source_id,
            source_node=source_node,
            target_node=target_node,
            source_location=(source_x, source_y, source_z),
            duration=duration,
            vt=vt,
        )

    def write(self, wr: m.Writer, context: Context) -> None:
        wr.write_object_id(self.target_id)
        wr.write_word(self.visual_effect_id)
        wr.write_float(self.target_location[0])
        wr.write_float(self.target_location[1])
        wr.write_float(self.target_location[2])

        if _vis_effect_uses_source(self.visual_effect_id, context):
            wr.write_object_id(self.source_id)
            wr.write_byte(self.source_node)
            wr.write_byte(self.target_node)
            wr.write_float(self.source_location[0])
            wr.write_float(self.source_location[1])
            wr.write_float(self.source_location[2])
            if self.target_id == INVALID_OBJECT_ID:
                wr.write_float(self.duration)

        m.write_dataclass(self.vt, wr, context)
