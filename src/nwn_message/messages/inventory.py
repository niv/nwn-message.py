from typing import Annotated
from dataclasses import dataclass

from .. import message as m

# All S2C Inventory messages share the prefix: item (ObjectId) + run_action_for_non_player (Bool).
# run_action_for_non_player=True means the action targets the creature in the "other" inventory
# panel (e.g. a henchman), rather than the player's own creature.


@dataclass(kw_only=True)
class InventoryEquip(m.Message):
    MAJOR = 0x0C
    MINOR = 0x01
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    run_action_for_non_player: m.Bool
    equip_slot: m.Dword


@dataclass(kw_only=True)
class InventoryEquipC2S(m.Message):
    MAJOR = 0x0C
    MINOR = 0x01
    DIRECTION = m.Direction.C2S

    item: m.ObjectId
    creature: m.ObjectId  # INVALID_OBJECT_ID for own creature
    equip_slot: m.Dword


@dataclass(kw_only=True)
class InventoryEquipCancel(m.Message):
    MAJOR = 0x0C
    MINOR = 0x02
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    run_action_for_non_player: m.Bool
    equip_slot: m.Dword


@dataclass(kw_only=True)
class InventoryDrop(m.Message):
    MAJOR = 0x0C
    MINOR = 0x03
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    run_action_for_non_player: m.Bool


@dataclass(kw_only=True)
class InventoryDropC2S(m.Message):
    MAJOR = 0x0C
    MINOR = 0x03
    DIRECTION = m.Direction.C2S

    item: m.ObjectId
    position: m.Vec3


@dataclass(kw_only=True)
class InventoryDropCancel(m.Message):
    MAJOR = 0x0C
    MINOR = 0x04
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    run_action_for_non_player: m.Bool


@dataclass(kw_only=True)
class InventoryPickup(m.Message):
    MAJOR = 0x0C
    MINOR = 0x05
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    run_action_for_non_player: m.Bool


@dataclass(kw_only=True)
class InventoryPickupC2S(m.Message):
    MAJOR = 0x0C
    MINOR = 0x05
    DIRECTION = m.Direction.C2S

    item: m.ObjectId
    target_repository: m.ObjectId
    x: m.Byte
    y: m.Byte


@dataclass(kw_only=True)
class InventoryPickupCancel(m.Message):
    MAJOR = 0x0C
    MINOR = 0x06
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    run_action_for_non_player: m.Bool


@dataclass(kw_only=True)
class InventoryUnequip(m.Message):
    MAJOR = 0x0C
    MINOR = 0x07
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    run_action_for_non_player: m.Bool


@dataclass(kw_only=True)
class InventoryUnequipC2S(m.Message):
    MAJOR = 0x0C
    MINOR = 0x07
    DIRECTION = m.Direction.C2S

    item: m.ObjectId
    target_repository: m.ObjectId
    x: m.Byte
    y: m.Byte


@dataclass(kw_only=True)
class InventoryUnequipCancel(m.Message):
    MAJOR = 0x0C
    MINOR = 0x08
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    run_action_for_non_player: m.Bool


@dataclass(kw_only=True)
class InventoryRepositoryMove(m.Message):
    MAJOR = 0x0C
    MINOR = 0x09
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    run_action_for_non_player: m.Bool


@dataclass(kw_only=True)
class InventoryRepositoryMoveC2S(m.Message):
    MAJOR = 0x0C
    MINOR = 0x09
    DIRECTION = m.Direction.C2S

    item: m.ObjectId
    target_repository: m.ObjectId
    x: m.Byte
    y: m.Byte


@dataclass(kw_only=True)
class InventoryRepositoryMoveCancel(m.Message):
    MAJOR = 0x0C
    MINOR = 0x0A
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    run_action_for_non_player: m.Bool


@dataclass(kw_only=True)
class InventoryEquipToggle(m.Message):
    MAJOR = 0x0C
    MINOR = 0x0B
    DIRECTION = m.Direction.C2S

    item: m.ObjectId
    has_secondary: m.Bool
    secondary: Annotated[m.ObjectId, m.IfEq("has_secondary", True)]


@dataclass(kw_only=True)
class InventoryUse(m.Message):
    MAJOR = 0x0C
    MINOR = 0x0C
    DIRECTION = m.Direction.C2S

    item: m.ObjectId


@dataclass(kw_only=True)
class InventoryLearnScroll(m.Message):
    MAJOR = 0x0C
    MINOR = 0x0D
    DIRECTION = m.Direction.C2S

    scroll: m.ObjectId


@dataclass(kw_only=True)
class InventoryLearnScrollSuccess(m.Message):
    MAJOR = 0x0C
    MINOR = 0x0E
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    run_action_for_non_player: m.Bool


@dataclass(kw_only=True)
class InventoryConfirmDrop(m.Message):
    MAJOR = 0x0C
    MINOR = 0x0F
    DIRECTION = m.Direction.S2C

    item: m.ObjectId
    run_action_for_non_player: m.Bool
